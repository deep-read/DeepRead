
import argparse
from collections import namedtuple
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--class-int',
        type=int,
        help='Int of class to rename',
        required=True,
    )
    parser.add_argument(
        '--class-new-name',
        type=int,
        help='Int of class new name',
        required=True,
    )
    parser.add_argument(
        '--label-dir',
        type=str,
        help='Path to folder containing the labels',
        required=True,
    )
    args = parser.parse_args()

    labels_dir = Path(args.label_dir)

    label = namedtuple('Label', 'label_index x_centre y_center width height')
    for label_file in labels_dir.iterdir():
        if label_file.stem != '.DS_Store':
            with open(label_file, 'r') as in_file:
                lines = []
                for line in in_file:
                    image_label = label(*line.strip().split())
                    if int(image_label.label_index) == args.class_int:
                        lines.append(
                            f'{int(args.class_new_name)} '
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
