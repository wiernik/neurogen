import argparse
import sys
from ChildProject.annotations import AnnotationManager
from ChildProject.projects import ChildProject
from ChildProject.pipelines.metrics import Metrics
from ChildProject.pipelines.metricsFunctions import simple_CTC_ph, simple_CTC, metricFunction
from functools import partial
import pandas as pd

def overlap_dur(annotations: pd.DataFrame, duration: int,
                interlocutors=('FEM', 'MAL', 'OCH', 'CHI'), **kwargs):
    """
    Computes the cumulated duration of overlapping speech
    """
    if annotations.empty:
        return 0

    interlocutors = set(interlocutors)
    annotations = annotations[annotations["speaker_type"].isin(interlocutors)].copy()
    annotations = annotations.sort_values('segment_onset')

    all_time_points = sorted(set(annotations['segment_onset']).union(set(annotations['segment_offset'])))
    total_overlap_duration = 0
    for i in range(len(all_time_points) - 1):
        interval_start = all_time_points[i]
        interval_end = all_time_points[i + 1]
        interval_duration = interval_end - interval_start
        active_speakers = 0
        for _, row in annotations.iterrows():
            # A speaker is active if their segment covers this interval
            if row['segment_onset'] <= interval_start and row['segment_offset'] >= interval_end:
                active_speakers += 1
        if active_speakers > 1:
            total_overlap_duration += interval_duration
    return total_overlap_duration

overlap_dur = metricFunction(set(), {"speaker_type"})(overlap_dur)

def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing its and vtc folders')
    parser.add_argument('--measures_file', type=str, required=True, help='Path to the .csv file containing the measures to extract')
    parser.add_argument('--output', type=str, required=True, help='Path to the output .csv file.')
    parser.add_argument('--only_human_annotated', action='store_true',
                        help='If activated, will only extract metrics for files that have been human annotated.')
    args = parser.parse_args(argv)

    project = ChildProject(args.data_path)

    # 1. Overwrite simple_CTC so that only a turn between an adult speaker and the key child counts as a turn
    my_lena_CTC_ph = partial(simple_CTC_ph, interlocutors_2=('FEM', 'MAL'))
    my_lena_CTC = partial(simple_CTC, interlocutors_2=('FEM', 'MAL'))
    my_overlap_dur = partial(overlap_dur, interlocutors=('FEM', 'MAL', 'CHI', 'OCH'))

    list_metrics = pd.read_csv(args.measures_file)
    list_metrics.loc[list_metrics['callable'] == 'simple_CTC_ph', 'callable'] = my_lena_CTC_ph
    list_metrics.loc[list_metrics['callable'] == 'simple_CTC', 'callable'] = my_lena_CTC
    list_metrics.loc[list_metrics['callable'] == 'overlap_dur', 'callable'] = my_overlap_dur


    if args.only_human_annotated:
        am = AnnotationManager(project)
        segments = am.annotations.loc[am.annotations['set'] == 'eaf/an1'][['recording_filename', 'range_onset', 'range_offset']]
        segments.columns = ['recording_filename', 'segment_onset', 'segment_offset']
        metrics = Metrics(project, segments=segments, by='segments', metrics_list=list_metrics).extract()
    else:
        metrics = Metrics(project, metrics_list=list_metrics).extract()

    metrics.to_csv(args.output, index=False)
    print(f"Saving results to {args.output}.")

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)