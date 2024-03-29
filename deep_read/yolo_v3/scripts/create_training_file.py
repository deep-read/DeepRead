""" Generates the train.txt used by YOLO """

import os
from pathlib import Path

import numpy as np

np.random.seed(42)

DATA_DIR = Path(f'{os.getcwd()}\data')
CONFIG_DIR = Path('.\data\model_config')

object_files = os.listdir(DATA_DIR/'labelled_images')
image_files = os.listdir(DATA_DIR/'book_covers')

with open(CONFIG_DIR/'train.txt', 'w') as out_file, open(CONFIG_DIR/'valid.txt', 'w') as valid_file:
    for f in object_files:
        if f != 'classes.txt' and f.endswith('.txt'):
            f = f.replace('.txt', '')
            for image in image_files:
                if f in image:
                    image_name = image
                    if np.random.sample() > 0.1:
                        out_file.write(f'{DATA_DIR}\\book_covers\\{image_name}\n')
                    else:
                        valid_file.write(f'{DATA_DIR}\\book_covers\\{image_name}\n')
                    break
            else:
                print(f'Image not found: {f}')
