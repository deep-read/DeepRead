""" Creates a custom YOLO model """

import argparse

from cv_training_stack.object_detection.yolo_v3.config.models import model_schemas

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-name',
        type=str,
        default='yolo_v3',
        help='Which yolo model to generate the schema of',
    )
    parser.add_argument(
        '--n-classes',
        type=int,
        required=True,
        help='The number of classes in your data set',
    )
    parser.add_argument(
        '--out-file',
        type=str,
        default='yolo_v3_custom.cfg',
        help='Name of file to write schema to',
    )

    args = parser.parse_args()
    print(args)

    if args.model_name == 'yolo_v3':
        model = model_schemas.yolo_v3(args.n_classes)
    else:
        model = model_schemas.yolo_v3(args.n_classes)

    with open(args.out_file, 'w') as file_out:
        file_out.write(model)
