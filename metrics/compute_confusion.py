import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_grid, conf_matrix
from ChildProject.projects import ChildProject
from tqdm import tqdm

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing the annotations folder')
    parser.add_argument('--set1', type=str, choices=['vtc', 'its', 'eaf/an1'],
                        help='First set to consider. Should belong to [vtc, its, eaf/an1].')
    parser.add_argument('--set2', type=str, choices=['vtc', 'its', 'eaf/an1'],
                        help='Second set to consider. Should belong to [vtc, its, eaf/an1].')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    project = ChildProject(data_path)
    am = AnnotationManager(project)
    speakers = ['CHI', 'OCH', 'MAL', 'FEM']
    am.read()

    set1_name = args.set1.replace('/', '_')
    set2_name = args.set2.replace('/', '_')
    result_path = Path(sys.path[0]).parent / 'results' / 'conf' / f'{set1_name}_{set2_name}'
    result_path.mkdir(exist_ok=True, parents=True)

    intersection = AnnotationManager.intersection(am.annotations, [args.set1, args.set2])


    tt = intersection[intersection['recording_filename'] == '20200312_145204_022874.wav']

    group_ids = list(project.children['group_id'].unique())
    group_ids.append('all')

    for group_id in group_ids:
        print(f"Computing confusion matrix for group: {group_id}")
        if group_id == 'all':
            group_intersection = intersection
        else:
            authorized_child_ids = project.children.loc[project.children['group_id'] == group_id, 'child_id'].unique()
            authorized_recordings = project.recordings.loc[project.recordings['child_id'].isin(authorized_child_ids), 'recording_filename'].unique()
            group_intersection = intersection[intersection['recording_filename'].isin(authorized_recordings)]

        if len(group_intersection) != 0:
            segments = am.get_collapsed_segments(group_intersection)
            set1 = segments_to_grid(segments[segments['set'] == args.set1], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
            set2 = segments_to_grid(segments[segments['set'] == args.set2], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
            confusion_counts = conf_matrix(set1, set2)
            np.save(result_path/ f'conf_{group_id}.npy', confusion_counts)
        else:
            print(f"Found 0 files annotated in the {group_id} group. Skipping.")

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)