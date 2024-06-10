import argparse
import sys
from pathlib import Path

import numpy as np
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_grid, conf_matrix
from ChildProject.projects import ChildProject


def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing its and vtc folders')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    project = ChildProject(data_path)
    am = AnnotationManager(project)
    speakers = ['CHI', 'OCH', 'MAL', 'FEM']
    am.read()

    intersection = AnnotationManager.intersection(am.annotations, ['vtc', 'its'])

    group_ids = list(project.children['group_id'].unique())
    group_ids.append('all')
    result_path = Path(sys.path[0]) / 'results'
    result_path.mkdir(exist_ok=True)

    for group_id in group_ids:
        print(f"Computing confusion matrix for group: {group_id}")
        if group_id == 'all':
            group_intersection = intersection
        else:
            authorized_child_ids = project.children.loc[project.children['group_id'] == group_id, 'child_id'].unique()
            authorized_recordings = project.recordings.loc[project.recordings['child_id'].isin(authorized_child_ids), 'recording_filename'].unique()
            group_intersection = intersection[intersection['recording_filename'].isin(authorized_recordings)]

        segments = am.get_collapsed_segments(group_intersection)
        vtc = segments_to_grid(segments[segments['set'] == 'vtc'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
        its = segments_to_grid(segments[segments['set'] == 'its'], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
        confusion_counts = conf_matrix(vtc, its)
        np.save(result_path/ f'conf_{group_id}.npy', confusion_counts)


if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)