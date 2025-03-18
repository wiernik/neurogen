import argparse
import sys
from ChildProject.annotations import AnnotationManager
from ChildProject.projects import ChildProject
from ChildProject.pipelines.metrics import Metrics
from ChildProject.pipelines.metricsFunctions import simple_CTC_ph, simple_CTC
from functools import partial
import pandas as pd

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
    list_metrics = pd.read_csv(args.measures_file)
    list_metrics.loc[list_metrics['callable'] == 'simple_CTC_ph', 'callable'] = my_lena_CTC_ph
    list_metrics.loc[list_metrics['callable'] == 'simple_CTC', 'callable'] = my_lena_CTC


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