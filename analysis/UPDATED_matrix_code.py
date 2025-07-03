
# note: i still want to streamline this by making things less chunky, but it works
# things i plan to add to clean up the code include:
    # using pandas merge so all the dict and csv file naming stuff can be smoother 
    # making it way easier to switch from vcmnet to meg's classifier, since this one just looks at vcmnet
        # i think it would be easier and more reproducible to have vcmnet and meg's classifier as arguments
        # and this code restructured w argparse instead. i didn't start out doing that because i wanted to
        # get a handle on the functionality first!
    # potentially creating a functions file that gets called since there are a few defined fx here
        # and these functions apply to each classifier (e.g., id want to clean the labels everywhere)
        # so its more 'universal' for the data we have in that sense

####################### packages & setup #######################

import os
from pathlib import Path
import pandas as pd
# from collections import Counter ---> put this back in for label/matrix counting debugging; code to do this in counting_debug.py

base_dir = Path(r'C:\Users\lydia\L3_HIPAA_LENA') # will be updating to relative path
subpaths = {
    "VCMNet": ['annotations', 'vcm', 'converted_from_human_timestamps'], #750 csvs found
    "meg_classifier": ['annotations', 'meg_vcm', 'converted_from_human_timestamps'], #750 csvs found
    "human_annotations": ['annotations', 'eaf', 'an1', 'converted'],  #750 csvs found
}

# dict accessible by filename as key
csv_files = {
    name: list((base_dir.joinpath(*parts)).glob('*.csv'))
    for name, parts in subpaths.items()
}

# easy access csv files per type
vcm_files = csv_files['VCMNet']
human_files = csv_files['human_annotations']
meg_files = csv_files['meg_classifier']  

# access variables for the future segment matching function
vcm_lookup = {os.path.basename(f): f for f in vcm_files}
human_lookup = {os.path.basename(f): f for f in human_files}
meg_lookup = {os.path.basename(f): f for f in meg_files} 

####################### SET UP FUNCTIONS #######################

# get rid of shorter segments
def remove_shorter_segments(df, min_duration_ms=60): 
    return df[(df['segment_offset'] - df['segment_onset']) >= min_duration_ms]
 
# match segments by onset/offset
def segments_match(row1, row2, onset_col='segment_onset', offset_col='segment_offset'): # no tolerance - exact matches only
    return (
        row1[onset_col] == row2[onset_col] and
        row1[offset_col] == row2[offset_col]
    )

####################### MATCH SEGMENTS AND CREATE LABEL PAIRS #######################

# this will store pairs of labels in tuples of (real, predicted)
label_pairs = []

for human_path in human_files:
    filename = os.path.basename(human_path) # from human -> vcm file / meg as needed

    # read the corresponding VCMNet file from whatver the human file is 
    df_vcm = pd.read_csv(vcm_lookup[filename])
    # filter for CHI speaker type and include only relevant columns
    df_vcm = df_vcm[df_vcm['speaker_type'] == 'CHI'][['segment_onset', 'segment_offset', 'vcm_type']]
    # remove segments shorter than 60 ms
    df_vcm = remove_shorter_segments(df_vcm)

    # same pipeline, but with human file
    df_human = pd.read_csv(human_path)
    df_human = df_human[df_human['speaker_type'] == 'CHI'][['segment_onset', 'segment_offset', 'vcm_type']]
    df_human = remove_shorter_segments(df_human)  

    matches_in_file = 0

    for _, human_row in df_human.iterrows(): # dont care about indices; iterate through rows for segment matches
        for _, vcm_row in df_vcm.iterrows():
            if segments_match(human_row, vcm_row):
                pair = (human_row['vcm_type'], vcm_row['vcm_type']) # real, predicted
                label_pairs.append(pair)
                matches_in_file += 1 
                break

# label_pairs = [(str(human), str(vcm)) for human, vcm in label_pairs] -> accidentally introduced nan

####################### comment the below out if you want ALL labels (N, C, L, Y, U) #######################

# # because we want to exclude any n/a or nan or missing labels
# def clean_label(label):
#     if pd.isna(label):
#         return None
#     return str(label).strip().lower()

# # because we want to exclude the labels that don't have any VCMNet annotations
# def contains_excluded_chars(label):
#     return 'l' in label or 'u' in label

# cleaned_label_pairs = [
#     (clean_label(human), clean_label(vcmnet))
#     for human, vcmnet in label_pairs
#     if pd.notna(human) and pd.notna(vcmnet)
#        and not contains_excluded_chars(clean_label(human))
#        and not contains_excluded_chars(clean_label(vcmnet))
# ]

# label_pairs = cleaned_label_pairs  # reassign
# labels = sorted(set(label for pair in label_pairs for label in pair))

####################### comment the above out if you want ALL labels (N, C, L, Y, U) #######################

####################### below label pairs contain ALL labels (N, C, L, Y, U) #######################

# no n/a or nan etc.
def clean_label(label):
    if pd.isna(label):
        return None
    return str(label).strip().lower()

cleaned_label_pairs = [
    (clean_label(human), clean_label(vcmnet))
    for human, vcmnet in label_pairs
    if pd.notna(human) and pd.notna(vcmnet)
]

label_pairs = cleaned_label_pairs # reassign to update
labels = sorted(set(label for pair in label_pairs for label in pair))

####################### above label pairs contain ALL labels (N, C, L, Y, U) #######################

####################### confusion matrix #######################

VCMNet_human_confusion_matrix = pd.DataFrame(0, index=labels, columns=labels)

for human_label, vcm_label in label_pairs:
    VCMNet_human_confusion_matrix.loc[human_label, vcm_label] += 1

VCMNet_human_confusion_matrix.to_csv("ALL_vcmnet_human_matrix.csv")

confusion_normalized = VCMNet_human_confusion_matrix.div(VCMNet_human_confusion_matrix.sum(axis=1), axis=0) * 100 # normalize by row and multiply by 100 for percentage
confusion_normalized.to_csv("ALL_vcmnet_human_matrix_normalised.csv")