import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_grid, conf_matrix
from ChildProject.metrics import segments_to_annotation

from ChildProject.projects import ChildProject
from tqdm import tqdm
from sklearn.metrics import cohen_kappa_score

def compute_kappa(set1, set2):
    classes = ['CHI', 'OCH', 'MAL', 'FEM', 'SIL']
    agreement_dict = {}
    for idx_spk, spk in enumerate(classes):
        set1_output = set1[:, idx_spk]
        set2_output = set2[:, idx_spk]

        # Compute agreement rate as:
        # number of frames labeled as K by both solutions
        # divided by number of frames labeled as K by either solution
        nb_frames_agreed = np.sum((set1_output == 1) & (set2_output == 1))
        nb_frames_either = np.sum((set1_output == 1) | (set2_output == 1))

        if nb_frames_either == 0:
            agreement_rate = 1
            kappa = 1
        else:
            agreement_rate = nb_frames_agreed / nb_frames_either
            kappa = cohen_kappa_score(set1_output, set2_output)

        agreement_dict[f'agreement_rate_{spk}'] = agreement_rate
        agreement_dict[f'kappa_{spk}'] = kappa
    return agreement_dict

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing the annotations folder')
    parser.add_argument('--set1', type=str, choices=['vtc', 'its'],
                        help='First set to consider. Should belong to [vtc, its, eaf/an1].')
    parser.add_argument('--set2', type=str, choices=['vtc', 'its', 'eaf/an1'],
                        help='Second set to consider. Should belong to [vtc, its, eaf/an1].')
    parser.add_argument('--two_mn_clip_level', action='store_true',
                        help='If activated, will also compute metrics at the 2-mn clip level.')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    project = ChildProject(data_path)
    am = AnnotationManager(project)
    speakers = ['CHI', 'OCH', 'MAL', 'FEM']
    am.read()

    intersection = AnnotationManager.intersection(am.annotations, [args.set1, args.set2])
    set1_name = args.set1
    set2_name = args.set2.replace('/', '_')
    result_path = Path(sys.path[0]).parent / 'results' / 'agreement' / f'{set1_name}_{set2_name}'
    result_path.mkdir(exist_ok=True, parents=True)

    recording_filenames = am.annotations.loc[am.annotations['set'] == 'eaf/an1']['recording_filename'].unique()

    which_group = project.recordings.merge(project.children, how='left', on='child_id')[['group_id', 'recording_filename']]
    which_group = which_group.set_index('recording_filename')['group_id'].to_dict()

    out = []
    for recording_id in tqdm(recording_filenames):
        group = which_group[recording_id]
        recording_intersection = intersection[intersection['recording_filename'] == recording_id]
        segments = am.get_collapsed_segments(recording_intersection)
        id_dict = {'recording_filename': recording_id, 'group_id': group}

        if len(segments) > 0:
            segments = segments[segments['speaker_type'].isin(speakers)]
            set1 = segments_to_grid(segments[segments['set'] == args.set1], 0, segments['segment_offset'].max(), 100,
                                    'speaker_type', speakers)
            set2 = segments_to_grid(segments[segments['set'] == args.set2], 0, segments['segment_offset'].max(), 100,
                                    'speaker_type', speakers)

            kappa_dict = compute_kappa(set1, set2)
        else:
            # Both solutions returned nothing: score is perfect
            kappa_dict = {
                'recording_filename': recording_id,
                'agreement_rate_CHI': 1, 'kappa_CHI': 1,
                'agreement_rate_OCH': 1, 'kappa_OCH': 1,
                'agreement_rate_MAL': 1, 'kappa_MAL': 1,
                'agreement_rate_FEM': 1, 'kappa_FEM': 1,
                'agreement_rate_SIL': 1, 'kappa_SIL': 1,
            }
        out.append({**id_dict, **kappa_dict})
    pd.DataFrame(out).to_csv(result_path / 'kappa_30mn_clips.csv', index=False)
    print('Saving results to', result_path / f'kappa_30mn_clips.csv')

    if args.two_mn_clip_level:
        segments = am.annotations.loc[am.annotations['set'] == 'eaf/an1'][['recording_filename', 'range_onset', 'range_offset']]

        out = []
        for idx, row in tqdm(segments.iterrows()):
            recording_filename = row['recording_filename']
            onset = row['range_onset']
            offset = row['range_offset']
            group = which_group[recording_filename]
            id_dict = {'recording_filename': recording_filename, 'group_id': group, 'onset': onset, 'offset': offset}
            recording_intersection = intersection[intersection['recording_filename'] == recording_filename]
            recording_intersection = recording_intersection[
                (recording_intersection['range_onset'] == onset) & (recording_intersection['range_offset'] == offset)]
            segments = am.get_collapsed_segments(recording_intersection)
            if len(segments) > 0 and len(segments[segments['speaker_type'].isin(speakers)]) > 0:
                segments = segments[segments['speaker_type'].isin(speakers)]
                set1 = segments_to_grid(segments[segments['set'] == args.set1], 0, segments['segment_offset'].max(),
                                        100,
                                        'speaker_type', speakers)
                set2 = segments_to_grid(segments[segments['set'] == args.set2], 0, segments['segment_offset'].max(),
                                        100,
                                        'speaker_type', speakers)
                kappa_dict = compute_kappa(set1, set2)
            else:
                # Both solutions returned nothing: score is perfect
                kappa_dict = {
                    'recording_filename': recording_filename,
                    'agreement_rate_CHI': 1, 'kappa_CHI': 1,
                    'agreement_rate_OCH': 1, 'kappa_OCH': 1,
                    'agreement_rate_MAL': 1, 'kappa_MAL': 1,
                    'agreement_rate_FEM': 1, 'kappa_FEM': 1,
                    'agreement_rate_SIL': 1, 'kappa_SIL': 1,
                }
            out.append({**id_dict, **kappa_dict})
        pd.DataFrame(out).to_csv(result_path / 'kappa_2mn_clips.csv', index=False)
        print('Saving results to', result_path / f'kappa_2mn_clips.csv')

    # if args.only_human_annotated:
    #     # Then we compute agreement over the 2-mn chunks annotated by humans
    #     segments_to_consider = am.annotations.loc[am.annotations['set'] == 'eaf/an1'][
    #         ['recording_filename', 'range_onset', 'range_offset']]
    # else:
    #     # Then we compute agreement over the recordings
    #     unique_filenames = project.recordings['recording_filename'].unique()
    #     segments_to_consider = pd.DataFrame({
    #         'recording_filename': unique_filenames,
    #         'range_onset': None,
    #         'range_offset': None
    #     })
    # processed = []
    # for idx, row in tqdm(segments_to_consider.iterrows()):
    #     recording_id = row['recording_filename']
    #     onset, offset = row['range_onset'], row['range_offset']
    #     if recording_id not in processed:
    #         recording_intersection = intersection[intersection['recording_filename'] == recording_id]
    #         if onset is not None and offset is not None:
    #             recording_intersection = recording_intersection[(recording_intersection['range_offset'] == offset) & (recording_intersection['range_onset'] == onset)]
    #
    #         segments = am.get_collapsed_segments(recording_intersection)
    #
    #         if len(segments) != 0:
    #             dur = offset-onset if onset is not None else segments['segment_offset'].max()
    #             set1 = segments_to_grid(segments[segments['set'] == args.set1], 0, dur, 100, 'speaker_type', speakers)
    #             set2 = segments_to_grid(segments[segments['set'] == args.set2], 0, dur, 100, 'speaker_type', speakers)
    #             classes = ['CHI', 'OCH', 'MAL', 'FEM', 'SIL']
    #             agreement_dict = {'recording_filename': recording_id, 'range_onset': onset, 'range_offset': offset}
    #             for idx_spk, spk in enumerate(classes):
    #                 set1_output = set1[:, idx_spk]
    #                 set2_output = set2[:, idx_spk]
    #
    #                 # Compute agreement rate as:
    #                 # number of frames labeled as K by both solutions
    #                 # divided by number of frames labeled as K by either solution
    #                 nb_frames_agreed = np.sum((set1_output == 1) & (set2_output == 1))
    #                 nb_frames_either = np.sum((set1_output == 1) | (set2_output == 1))
    #
    #                 if nb_frames_either == 0:
    #                     agreement_rate = 1
    #                     kappa = 1
    #                 else:
    #                     agreement_rate = nb_frames_agreed / nb_frames_either
    #                     kappa = cohen_kappa_score(set1_output, set2_output)
    #
    #                 agreement_dict[f'agreement_rate_{spk}'] = agreement_rate
    #                 agreement_dict[f'kappa_{spk}'] = kappa
    #
    #             out.append(agreement_dict)
    #         else:
    #             out.append({'recording_filename': recording_id, 'range_onset': onset, 'range_offset': offset,
    #                         'agreement_rate_CHI': 1, 'kappa_CHI': 1,
    #                         'agreement_rate_OCH': 1, 'kappa_OCH': 1,
    #                         'agreement_rate_MAL': 1, 'kappa_MAL': 1,
    #                         'agreement_rate_FEM': 1, 'kappa_FEM': 1,
    #                         'agreement_rate_SIL': 1, 'kappa_SIL': 1,
    #                         })
    #         pd.DataFrame(out).to_csv(result_path / 'agreement_file_level.csv', index=False)



if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)