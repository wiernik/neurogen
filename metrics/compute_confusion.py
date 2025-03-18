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
    parser.add_argument('--file_level', action='store_true',
                        help='If activated, will store file-level confusion matrices in a csv file.')
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
    result_path = Path(sys.path[0]) / 'results' / 'conf' / f'{set1_name}_{set2_name}'
    result_path.mkdir(exist_ok=True, parents=True)

    intersection = AnnotationManager.intersection(am.annotations, [args.set1, args.set2])

    if args.file_level:
        recording_ids = list(project.recordings['recording_filename'].unique())

        if (result_path / 'conf_file_level.csv').is_file():
            out = pd.read_csv(result_path / 'conf_file_level.csv')
            processed = out['recording_filename'].tolist()
            out = out.to_dict('records')
        else:
            processed = []
            out = []

        for recording_id in tqdm(recording_ids):
            if recording_id not in processed:
                recording_intersection = intersection[intersection['recording_filename'] == recording_id]
                segments = am.get_collapsed_segments(recording_intersection)
                set1 = segments_to_grid(segments[segments['set'] == args.set1], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
                set2 = segments_to_grid(segments[segments['set'] == args.set2], 0, segments['segment_offset'].max(), 100, 'speaker_type', speakers)
                confusion_counts = conf_matrix(set1, set2)
                nb_frames_set1 = confusion_counts.sum(axis=1)
                nb_frames_set2 = confusion_counts.sum(axis=0)
                conf_speakers = ['CHI', 'OCH', 'MAL', 'FEM', 'SIL']
                confusion_dict1 = {f'{args.set1}_{conf_speakers[i]}_{args.set2}_{conf_speakers[j]}': confusion_counts[i][j] for i in range(len(conf_speakers)) for j in range(len(conf_speakers))}
                confusion_dict2 = {f'nb_frames_{args.set2}_{conf_speakers[i]}': nb_frames_set2[i] for i in range(len(conf_speakers))}
                confusion_dict3 = {f'nb_frames_{args.set1}_{conf_speakers[i]}': nb_frames_set1[i] for i in range(len(conf_speakers))}
                confusion_dict = {'recording_filename': recording_id}
                confusion_dict.update(confusion_dict1)
                confusion_dict.update(confusion_dict2)
                confusion_dict.update(confusion_dict3)
                out.append(confusion_dict)
                pd.DataFrame(out).to_csv(result_path / 'conf_file_level.csv', index=False)
    else:
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
                print(segments[segments['set'] == args.set1][['set', 'segment_onset', 'segment_offset', 'recording_filename', 'duration']])
                print(segments[segments['set'] == args.set2][['set', 'segment_onset', 'segment_offset', 'recording_filename', 'duration']])
                print(segments.columns)
                exit()
                confusion_counts = conf_matrix(set1, set2)
                np.save(result_path/ f'conf_{group_id}.npy', confusion_counts)
            else:
                print(f"Found 0 files annoated in the {group_id} group. Skipping.")


if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)