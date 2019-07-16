""" Generates the train.txt used by YOLO """

import os
from pathlib import Path

import numpy as np

np.random.seed(42)

DATA_DIR = Path(f'{os.getcwd()}/data/object_detection/smart_new_homes/iteration_1/processed')
CONFIG_DIR = Path('./cv_training_stack/object_detection/smart_new_homes/data_config')

object_files = os.listdir(DATA_DIR/'image_objects')
image_files = os.listdir(DATA_DIR/'images')

with open(CONFIG_DIR/'train.txt', 'w') as out_file, open(CONFIG_DIR/'valid.txt', 'w') as valid_file:
    for f in object_files:
        if f != 'classes.txt' and f.endswith('.txt'):
            f = f.replace('.txt', '')
            for image in image_files:
                if f in image:
                    image_name = image
                    if np.random.sample() > 0.1:
                        # out_file.write(f'{DATA_DIR}/all_images/{image_name}\n')
                        out_file.write(f'data/custom/images/{image_name}\n')
                    else:
                        # valid_file.write(f'{DATA_DIR}/all_images/{image_name}\n')
                        valid_file.write(f'data/custom/images/{image_name}\n')
                    break
            else:
                print(f'Image not found: {f}')
