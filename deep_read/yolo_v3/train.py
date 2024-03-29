
import os
import sys
if os.name == 'nt':
    sys.path.append(os.getcwd())
import time
import datetime
import argparse

from terminaltables import AsciiTable
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms
from torch.autograd import Variable
import torch.optim as optim

from deep_read.yolo_v3.models import Darknet
from deep_read.yolo_v3.utils.logger import *
from deep_read.yolo_v3.utils.utils import (
    load_classes,
    weights_init_normal,
)
from deep_read.yolo_v3.utils.datasets import (
    ListDataset
)
from deep_read.yolo_v3.utils.parse_config import (
    parse_data_config
)
from deep_read.yolo_v3.test import evaluate


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=100, help='number of epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='size of each image batch')
    parser.add_argument('--gradient-accumulations', type=int, default=2, help='number of gradient accums before step')
    parser.add_argument('--model-def', type=str, help='path to model definition file')
    parser.add_argument('--data-config', type=str, help='path to data config file')
    parser.add_argument('--pretrained-weights', type=str, help='if specified starts from checkpoint model')
    parser.add_argument('--n-cpu', type=int, default=8, help='number of cpu threads to use during batch generation')
    parser.add_argument('--img-size', type=int, default=416, help='size of each image dimension')
    parser.add_argument('--evaluation-interval', type=int, default=1, help='interval evaluations on validation set')
    parser.add_argument('--compute-map', default=False, help='if True computes mAP every tenth batch')
    parser.add_argument('--multiscale-training', default=True, help='allow for multi-scale training')
    opt = parser.parse_args()
    print(opt)

    # logger = Logger("logs")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    os.makedirs('output', exist_ok=True)

    # Get data configuration
    data_config = parse_data_config(opt.data_config)
    train_path = data_config['train']
    valid_path = data_config['valid']
    labels_path = data_config['boxes']
    class_names = load_classes(data_config['names'])

    # Initiate model
    model = Darknet(opt.model_def).to(device)
    model.apply(weights_init_normal)

    # If specified we start from pre-trained model
    if opt.pretrained_weights:
        model.load_darknet_weights(opt.pretrained_weights)

    # Get dataloader
    dataset = ListDataset(
        train_path,
        labels_path,
        augment=True,
        multiscale=opt.multiscale_training
    )
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=opt.batch_size,
        shuffle=True,
        num_workers=opt.n_cpu,
        pin_memory=True,
        collate_fn=dataset.collate_fn,
    )

    optimizer = torch.optim.Adam(model.parameters())

    metrics = [
        'grid_size',
        'loss',
        'x',
        'y',
        'w',
        'h',
        'conf',
        'cls',
        'cls_acc',
        'recall50',
        'recall75',
        'precision',
        'conf_obj',
        'conf_noobj',
    ]

    for epoch in range(opt.epochs):
        model.train()
        start_time = time.time()
        for batch_i, (_, imgs, targets) in enumerate(dataloader):

            batches_done = len(dataloader) * epoch + batch_i

            imgs = Variable(imgs.to(device))
            targets = Variable(targets.to(device), requires_grad=False)

            loss, outputs = model(imgs, targets)
            loss.backward()

            if batches_done % opt.gradient_accumulations:
                # Accumulates gradient before each step
                optimizer.step()
                optimizer.zero_grad()

            # ----------------
            #   Log progress
            # ----------------

            log_str = f'\n---- [Epoch {epoch + 1}/{opt.epochs}, Batch {batch_i}/{len(dataloader)}] ----\n'

            metric_table = [['Metrics', *[f'YOLO Layer {i}' for i in range(len(model.yolo_layers))]]]

            # Log metrics at each YOLO layer
            for i, metric in enumerate(metrics):
                formats = {m: '%.6f' for m in metrics}
                formats['grid_size'] = '%2d'
                formats['cls_acc'] = '%.2f%%'
                row_metrics = [formats[metric] % yolo.metrics.get(metric, 0) for yolo in model.yolo_layers]
                metric_table += [[metric, *row_metrics]]

                # # Tensorboard logging
                # tensorboard_log = []
                # for j, yolo in enumerate(model.yolo_layers):
                #     for name, metric in yolo.metrics.items():
                #         if name != "grid_size":
                #             tensorboard_log += [(f"{name}_{j+1}", metric)]
                # tensorboard_log += [("loss", loss.item())]
                # logger.list_of_scalars_summary(tensorboard_log, batches_done)

            log_str += AsciiTable(metric_table).table
            log_str += f'\nTotal loss {loss.item()}'

            # Determine approximate time left for epoch
            epoch_batches_left = len(dataloader) - (batch_i + 1)
            time_left = datetime.timedelta(seconds=epoch_batches_left * (time.time() - start_time) / (batch_i + 1))
            log_str += f'\n---- ETA {time_left}'

            print(log_str)

            model.seen += imgs.size(0)

        if epoch % opt.evaluation_interval == 0:
            print('\n---- Evaluating Model ----')
            # Evaluate the model on the validation set
            precision, recall, AP, f1, ap_class = evaluate(
                model,
                path=valid_path,
                labels_path=labels_path,
                iou_thres=0.2,
                conf_thres=0.5,
                nms_thres=0.2,
                img_size=opt.img_size,
                batch_size=8,
            )
            evaluation_metrics = [
                ('val_precision', precision.mean()),
                ('val_recall', recall.mean()),
                ('val_mAP', AP.mean()),
                ('val_f1', f1.mean()),
            ]
            # logger.list_of_scalars_summary(evaluation_metrics, epoch)

            # Print class APs and mAP
            ap_table = [['Index', 'Class name', 'AP']]
            for i, c in enumerate(ap_class):
                ap_table += [[c, class_names[c], '%.5f' % AP[i]]]
            print(AsciiTable(ap_table).table)
            print(f'---- mAP {AP.mean()}')

    model.save_darknet_weights('deep_read.weights')
