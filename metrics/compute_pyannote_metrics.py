import argparse
import sys
from pathlib import Path

import pandas as pd
from ChildProject.annotations import AnnotationManager
from ChildProject.metrics import segments_to_annotation
from ChildProject.projects import ChildProject
from pyannote.core import Timeline, Segment
from pyannote.metrics.detection import DetectionPrecisionRecallFMeasure
from pyannote.metrics.identification import IdentificationErrorRate
from tqdm import tqdm

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing the annotations folder')
    parser.add_argument('--hyp', type=str, choices=['vtc', 'its'],
                        help='Hypothesis set. Choose between vtc and its.')
    parser.add_argument('--ref', type=str, default='eaf/an1',
                        help='Reference set (default to eaf/an1)')
    parser.add_argument('--metric', type=str, choices=['ider', 'fscore'],
                        help='Reference set (default to eaf/an1)')
    parser.add_argument('--two_mn_clip_level', action='store_true',
                        help='If activated, will also compute metrics at the 2-mn clip level.')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    project = ChildProject(data_path)
    am = AnnotationManager(project)
    am.read()

    intersection = AnnotationManager.intersection(am.annotations, [args.hyp, args.ref])
    set1_name = args.hyp
    set2_name = args.ref.replace('/', '_')
    result_path = Path(sys.path[0]).parent / 'results' / 'pyannote_metrics' / f'{set1_name}_{set2_name}'
    result_path.mkdir(exist_ok=True, parents=True)

    speakers = ['CHI', 'OCH', 'FEM', 'MAL']
    recording_filenames = am.annotations.loc[am.annotations['set'] == 'eaf/an1']['recording_filename'].unique()

    which_group = project.recordings.merge(project.children, how='left', on='child_id')[['group_id', 'recording_filename']]
    which_group = which_group.set_index('recording_filename')['group_id'].to_dict()

    if args.metric == 'ider':
        metric = IdentificationErrorRate()
    elif args.metric == 'fscore':
        metric = DetectionPrecisionRecallFMeasure()

    out = []
    for recording_id in tqdm(recording_filenames):
        recording_intersection = intersection[intersection['recording_filename'] == recording_id]
        segments = am.get_collapsed_segments(recording_intersection)

        if len(segments) > 0:
            segments = segments[segments['speaker_type'].isin(speakers)]

        ref = segments_to_annotation(segments[segments['set'] == args.ref], 'speaker_type')
        hyp = segments_to_annotation(segments[segments['set'] == args.hyp], 'speaker_type')
        row = {'recording_id': recording_id, 'group_id': which_group[recording_id]}
        if args.metric == 'fscore':
            for speaker in speakers:
                ref_s = ref.subset([speaker])
                hyp_s = hyp.subset([speaker])
                detail_s = metric.compute_components(reference=ref_s, hypothesis=hyp_s)
                result_s = metric.compute_metric(detail=detail_s)
                metric.reset()
                detail_s = {f'{k}_{speaker}': v for k,v in detail_s.items()}
                row_s = {**detail_s, f'{args.metric}_{speaker}': result_s}
                row = {**row, **row_s}
        elif args.metric == 'ider':
            detail = metric.compute_components(reference=ref, hypothesis=hyp)
            result = metric.compute_metric(detail=detail)
            row = {**row, **detail, f'{args.metric}': result}
        out.append(row)

    pd.DataFrame(out).to_csv(result_path / f'{args.metric}_30mn_clips.csv', index=False)
    print('Saving results to', result_path / f'{args.metric}_30mn_clips.csv')

    if args.two_mn_clip_level:
        segments = am.annotations.loc[am.annotations['set'] == 'eaf/an1'][['recording_filename', 'range_onset', 'range_offset']]

        which_group = project.recordings.merge(project.children, how='left', on='child_id')[['group_id', 'recording_filename']]
        which_group = which_group.set_index('recording_filename')['group_id'].to_dict()

        out = []
        for idx, row in segments.iterrows():

            recording_filename = row['recording_filename']
            onset = row['range_onset']
            offset = row['range_offset']
            dur = (offset - onset)
            recording_intersection = intersection[intersection['recording_filename'] == recording_filename]
            recording_intersection = recording_intersection[
                (recording_intersection['range_onset'] == onset) & (recording_intersection['range_offset'] == offset)]

            segments = am.get_collapsed_segments(recording_intersection)
            if len(segments) > 0:
                segments = segments[segments['speaker_type'].isin(speakers)]
            ref = segments_to_annotation(segments[segments['set'] == args.ref], 'speaker_type')
            hyp = segments_to_annotation(segments[segments['set'] == args.hyp], 'speaker_type')

            row = {'recording_id': recording_filename, 'onset': onset, 'offset': offset,
                       'group_id': which_group[recording_filename]}
            if args.metric == 'fscore':
                for speaker in speakers:
                    ref_s = ref.subset([speaker])
                    hyp_s = hyp.subset([speaker])

                    detail_s = metric.compute_components(reference=ref_s, hypothesis=hyp_s,
                                                         uem=Timeline([Segment(0, dur)]))
                    result_s = metric.compute_metric(detail=detail_s)
                    metric.reset()
                    detail_s = {f'{k}_{speaker}': v for k,v in detail_s.items()}
                    row_s = {**detail_s, f'{args.metric}_{speaker}': result_s}
                    row = {**row, **row_s}
            elif args.metric == 'ider':
                detail = metric.compute_components(reference=ref, hypothesis=hyp, uem=Timeline([Segment(0,dur)]))
                result = metric.compute_metric(detail=detail)
                metric.reset()
                row = {**row, **detail, f'{args.metric}': result}
                metric.reset()
            out.append(row)

        pd.DataFrame(out).to_csv(result_path / f'{args.metric}_2mn_clips.csv', index=False)
        print('Saving results to', result_path / f'{args.metric}_2mn_clips.csv')




if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)