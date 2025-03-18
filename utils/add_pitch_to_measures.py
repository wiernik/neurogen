import sys
from pathlib import Path
import pandas as pd
import argparse
import numpy as np
from tqdm import tqdm
import parselmouth

def extract_CHI_pitch(clip_path, segmentation_path, clip_onset, clip_offset, min_pitch=200, max_pitch=800,
                      automatic=False, save=False):
    if not clip_path.exists():
        print(f"Cannot find {clip_path}")
        exit()
    if not segmentation_path.exists():
        print(f"Cannot find {segmentation_path}")
        exit()
    segmentation = pd.read_csv(segmentation_path)
    segmentation = segmentation[segmentation.speaker_type == 'CHI']

    if automatic:
        mask= (segmentation['segment_offset'] > clip_onset) & (segmentation['segment_onset'] < clip_offset)
        segmentation = segmentation[mask]
        segmentation['segment_onset'] = segmentation['segment_onset'].clip(lower=clip_onset)
        segmentation['segment_offset'] = segmentation['segment_offset'].clip(upper=clip_offset)

    audio_clip = parselmouth.Sound(str(clip_path))

    speechlike_pitch = []
    nonspeechlike_pitch = []
    for idx, row in segmentation.iterrows():
        segment_onset, segment_offset = int(row["segment_onset"]), int(row["segment_offset"])
        segment_onset -= clip_onset
        segment_offset -= clip_onset
        if 'vcm_type' in row:
            is_speech_like = row['vcm_type'] in ['C', 'N']
        else:
            is_speech_like = row['utterances_count'] > 0

        mean_pitch = np.nan
        if segment_offset - segment_onset > 100:
            voc = audio_clip.extract_part(from_time=segment_onset/1000, to_time=segment_offset/1000)
            pitch = voc.to_pitch(time_step=0.01,
                                 pitch_floor=min_pitch,
                                 pitch_ceiling=max_pitch)
            pitch_values = pitch.selected_array['frequency']

            # Calculate mean pitch (excluding unvoiced frames)
            voiced_pitch = pitch_values[pitch_values != 0]  # Remove unvoiced frames
            mean_pitch = np.mean(voiced_pitch) if len(voiced_pitch) > 0 else np.nan

            if save and not np.isnan(mean_pitch):
                # Create output directory if it doesn't exist
                save_dir = clip_path.parent / 'vocalizations'
                save_dir.mkdir(exist_ok=True)

                # Save with pitch as filename
                save_path = save_dir / f"{int(mean_pitch)}.wav"
                voc.save(str(save_path), 'WAV')

        if is_speech_like:
            speechlike_pitch.append(mean_pitch)
        else:
            nonspeechlike_pitch.append(mean_pitch)
    return speechlike_pitch, nonspeechlike_pitch


def main(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--annotation_folder', type=str,
                        help='Path to the annotation folder containing .csv segmentation files.')
    parser.add_argument('--audio_folder', type=str,
                        help='Path to the folder .wav 2-mn clips.')
    parser.add_argument('--measures_path', type=str,
                        help='Path to the .csv file with AWC, CTC, CVC measures.')
    parser.add_argument('--automatic', action='store_true',
                        help='Must be activated if LENA or ACLEW')
    args = parser.parse_args(argv)
    annotation_folder = Path(args.annotation_folder)
    audio_folder = Path(args.audio_folder)
    measures_path = Path(args.measures_path)

    # Load measures
    measures = pd.read_csv(measures_path, sep=',')
    measures = measures.sort_values(['recording_filename', 'segment_onset', 'segment_offset'])
    if 'speechlike_pitch' in measures.columns and 'nonspeechlike_pitch' in measures.columns:
        print("Already done.")
        exit()

    pitch_measures = []
    for idx, row in tqdm(measures.iterrows()):
        recording_filename = row['recording_filename']
        clip_onset = int(row['segment_onset'])
        clip_offset = int(row['segment_offset'])
        clip_path = audio_folder / f"{recording_filename.rstrip('.wav')}_{clip_onset}_{clip_offset}.wav"
        if args.automatic:
            segmentation_path = annotation_folder / f"{recording_filename.rstrip('.wav')}.csv"
        else:
            segmentation_path = annotation_folder / f"{recording_filename.rstrip('.wav')}_{clip_onset}_{clip_offset}.csv"
        speechlike_pitch, nonspeechlike_pitch = extract_CHI_pitch(clip_path, segmentation_path, clip_onset, clip_offset,
                                                                  automatic=args.automatic)
        pitch_measures.append({'recording_filename': recording_filename,
                               'segment_onset': clip_onset,
                               'segment_offset': clip_offset,
                               'speechlike_pitch': speechlike_pitch,
                               'nonspeechlike_pitch': nonspeechlike_pitch})

    pitch_measures = pd.DataFrame(pitch_measures)
    merged_measures = measures.merge(
        pitch_measures,
        on=['recording_filename', 'segment_onset', 'segment_offset'],
        how='left'  # Keep all rows from measures, even if no pitch data
    )


    merged_measures.to_csv(measures_path, index=False)

if __name__ == "__main__":
    # execute only if run as a script
    args = sys.argv[1:]
    main(args)