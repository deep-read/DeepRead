"""
Removes a given class from the classes.txt and all label files
"""

import argparse
from collections import namedtuple
from pathlib import Path
import os
import sys

from terminaltables import AsciiTable

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--class-name',
        type=str,
        help='Name of class to remove',
        required=True,
    )
    parser.add_argument(
        '--class-file',
        type=str,
        help='Path to class file including filename',
        required=True,
    )
    parser.add_argument(
        '--label-dir',
        type=str,
        help='Path to folder containing the labels',
        required=True,
    )
    args = parser.parse_args()

    class_name = args.class_name
    labels_dir = Path(args.label_dir)

    with open(args.class_file, 'r') as in_file:
        classes = [line.strip() for line in in_file if line]
        try:
            class_index = classes.index(class_name)
        except ValueError:
            raise ValueError(f'Class name \'{class_name}\' not in class file')

    table_data = [['Index', 'Class', 'Flagged for Removal']]
    for i, c in enumerate(classes):
        if i == class_index:
            table_data.append([i, c, 'Yes'])
        else:
            table_data.append([i, c, 'No'])

    table = AsciiTable(table_data)
    print(table.table)
    print(
        f'Index: {class_index} will be removed from the class file and from '
        f'any labelled files if found. Classes with indexes > 10 will be drop '
        f'an index value. '
        f'IT IS RECOMMENDED YOU MAKE A BACKUP BEFORE YOU PROCEED!'
    )
    while True:
        proceed = input('Continue? [y/n]:').lower()
        if proceed == 'y':
            break
        elif proceed == 'n':
            print('Not proceeding further, no files were changed')
            sys.exit()
        else:
            print('Invalid input, try again')

    with open(args.class_file, 'w') as out_file:
        for i, c in enumerate(classes):
            if i != class_index:
                out_file.write(f'{c}\n')

    label = namedtuple('Label', 'label_index x_centre y_center width height')
    for label_file in labels_dir.iterdir():
        if label_file.stem != '.DS_Store':
            with open(label_file, 'r') as in_file:
                lines = []
                for line in in_file:
                    image_label = label(*line.strip().split())
                    if image_label.label_index != str(class_index):
                        if int(image_label.label_index) > class_index:
                            lines.append(
                                f'{int(image_label.label_index) - 1} '
                                f'{image_label.x_centre} '
                                f'{image_label.y_center} '
                                f'{image_label.width} {image_label.height}\n'
                            )
                        else:
                            lines.append(line)
            if lines:
                with open(label_file, 'w') as out_f:
                    for line in lines:
                        out_f.write(line)
            else:
                os.remove(label_file)
