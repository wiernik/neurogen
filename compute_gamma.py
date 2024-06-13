import argparse
import sys
from pathlib import Path

import pandas as pd
from ChildProject.annotations import AnnotationManager
from ChildProject.projects import ChildProject
from pyannote.core import Segment
from pygamma_agreement.continuum import Continuum
from pygamma_agreement.dissimilarity import CombinedCategoricalDissimilarity
from tqdm import tqdm


def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--data_path', type=str, default='/home/engaclew/DATA/neurogen/L3_HIPAA_LENA_cleaned',
                        help='Path to the data containing its and vtc folders')
    args = parser.parse_args(argv)
    data_path = Path(args.data_path)
    project = ChildProject(data_path)
    am = AnnotationManager(project)

    am.read()
    intersection = AnnotationManager.intersection(am.annotations, ['vtc', 'its'])
    segments = am.get_collapsed_segments(intersection)
    segments = segments[~segments['speaker_type'].isna()]

    out = []
    recording_files = segments['recording_filename'].unique()
    for recording_file in tqdm(recording_files):
        file_segments = segments[segments['recording_filename'] == recording_file]
        continuum = Continuum()
        for segment in file_segments.to_dict(orient="records"):
            continuum.add(
                segment["set"],
                Segment(segment["segment_onset"]/1000, segment["segment_offset"]/1000),
                segment["speaker_type"],
            )
  
        dissim = CombinedCategoricalDissimilarity(delta_empty=1, alpha=1, beta=1)
        gamma_results = continuum.compute_gamma(dissim, precision_level=0.05, fast=True)
        gamma_dict = {
            'recording_filename': recording_file,
            'gamma': gamma_results.gamma,
            'gamma_cat': gamma_results.gamma_cat,
            'gamma_chi': gamma_results.gamma_k('CHI'),
            'gamma_och': gamma_results.gamma_k('OCH'),
            'gamma_mal': gamma_results.gamma_k('MAL'),
            'gamma_fem': gamma_results.gamma_k('FEM')
        }
        out.append(gamma_dict)

    print(f"Saving results to {Path(sys.path[0]) / 'results' / 'gamma' / 'gamma.csv'}")
    result_path = Path(sys.path[0]) / 'results' / 'gamma'
    result_path.mkdir(exist_ok=True, parents=True)
    pd.DataFrame(out).to_csv(result_path / 'gamma.csv', index=False)
    print("Done.")

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)