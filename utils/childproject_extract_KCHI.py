from ChildProject.projects import ChildProject
from ChildProject.annotations import AnnotationManager
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Create a csv files containing all KCHI segments with onset, offset, and recording_filename")
    parser.add_argument('--project', required=True, help='Path to ChildProject project (neurogen).')
    parser.add_argument('--set', required=True, choices=['vtc', 'its', 'eaf/an1'], help='Set from which KCHI segments need to be extracted')

    args = parser.parse_args()
    args.project = Path(args.project)
    proj = ChildProject(args.project)
    am = AnnotationManager(proj)
    am.read()

    anno = am.annotations[am.annotations['set'] == args.set]
    segments = am.get_segments(anno)

    kchi_segments = segments[segments['speaker_type'] == 'CHI']
    out_dir = args.project / 'samples' / 'chi'
    out_dir.mkdir(parents=True, exist_ok=True)
    set_name = args.set.replace('/', '_')
    kchi_segments[['recording_filename','segment_onset','segment_offset']].to_csv(args.project / 'samples' / 'chi' / f'segments_all_chi_{set_name}.csv' , index=False)

if __name__ == '__main__':
    main()