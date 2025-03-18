import argparse
import os
import random
from pathlib import Path
import pandas as pd
import soundfile as sf


# python extract_chunks.py --csv /scratch1/data/raw_data/neurogen/L3_HIPAA_LENA_cleaned/selected_recordings.csv --source /scratch1/data/raw_data/neurogen/L3_HIPAA_LENA_cleaned/recordings/raw --dest /scratch1/data/raw_data/neurogen/L3_HIPAA_LENA_cleaned/recordings/selected_chunks

def extract_random_chunks(input_file, num_chunks=15, chunk_duration=120, seed=42):
    """
    Extract random non-overlapping chunks from an audio file.
    Ensures chunks start at second boundaries (multiples of 1000ms).

    Args:
        input_file (str): Path to input audio file
        num_chunks (int): Number of chunks to extract
        chunk_duration (int): Duration of each chunk in seconds
        seed (int): Random seed for reproducible results (default: 42)

    Returns:
        list: List of dictionaries containing chunk information
    """
    # Set random seed
    random.seed(seed)

    # Read audio file
    audio_data, sample_rate = sf.read(input_file)

    # Calculate chunk size in samples
    chunk_size = chunk_duration * sample_rate

    # Calculate total possible chunks
    total_samples = len(audio_data)
    max_start = total_samples - chunk_size

    if max_start <= 0:
        print(f"Warning: {input_file} is too short for {chunk_duration}s chunks")
        return []

    # Calculate valid start positions (at second boundaries)
    possible_starts = list(range(0, max_start, sample_rate))
    if not possible_starts:
        print(f"Warning: {input_file} is too short for {chunk_duration}s chunks")
        return []

    # Generate non-overlapping chunks using the original algorithm first
    used_ranges = []
    chunks_info = []

    # Use a separate random generator with the same seed to recreate the exact same sequence
    original_random = random.Random(seed)

    # First, generate all chunks using the original algorithm to identify overlaps
    original_chunks = []
    for _ in range(num_chunks):
        # Remove already used start positions using original check
        available_starts = [start for start in possible_starts if not any(
            used_start <= start < used_end for used_start, used_end in used_ranges
        )]

        if not available_starts:
            print(f"Warning: Could not find space for chunk {_ + 1} in {input_file}")
            break

        # Choose random start position from available ones
        start_sample = original_random.choice(available_starts)
        end_sample = start_sample + chunk_size

        # Store the chunk
        original_chunks.append({
            'start_sample': start_sample,
            'end_sample': end_sample,
            'start_ms': int(start_sample / sample_rate * 1000),
            'end_ms': int(end_sample / sample_rate * 1000)
        })

        # Update used ranges
        used_ranges.append((start_sample, end_sample))

    # Now identify chunks that overlap with others
    overlapping_indices = set()
    for i in range(len(original_chunks)):
        for j in range(i + 1, len(original_chunks)):
            chunk_i = original_chunks[i]
            chunk_j = original_chunks[j]

            # Check if chunks overlap
            if (chunk_i['start_sample'] < chunk_j['end_sample'] and
                    chunk_i['end_sample'] > chunk_j['start_sample']):
                # These chunks overlap
                overlapping_indices.add(i)
                overlapping_indices.add(j)
                print(f"Found overlap between chunks {i} and {j}")

    # If there are no overlaps, return original chunks
    if not overlapping_indices:
        print("No overlapping chunks found.")
        return original_chunks

    # Reset for the final chunk selection
    used_ranges = []
    chunks_info = []

    # Add all non-overlapping chunks first (preserve their exact positions)
    for i, chunk in enumerate(original_chunks):
        if i not in overlapping_indices:
            chunks_info.append(chunk)
            used_ranges.append((chunk['start_sample'], chunk['end_sample']))

    # Now generate new positions only for the overlapping chunks
    random.seed(seed + 1)  # Use a different seed for the new selections

    while len(chunks_info) < len(original_chunks) and len(overlapping_indices) > 0:
        # Calculate all available start positions, excluding ranges that would overlap with existing chunks
        available_starts = []
        for start in possible_starts:
            # Calculate the end position if we were to start here
            potential_end = start + chunk_size

            # Check if this potential chunk would overlap with any existing chunk
            overlap = False
            for used_start, used_end in used_ranges:
                # Check for overlap: either the start or end falls within an existing chunk,
                # or the chunk completely contains an existing chunk
                if (used_start <= start < used_end) or \
                        (used_start < potential_end <= used_end) or \
                        (start <= used_start and potential_end >= used_end):
                    overlap = True
                    break

            if not overlap:
                available_starts.append(start)

        if not available_starts:
            print(f"Warning: Could not find space for a replacement chunk")
            break

        # Choose random start position from available ones
        start_sample = random.choice(available_starts)
        end_sample = start_sample + chunk_size
        used_ranges.append((start_sample, end_sample))

        # Convert to milliseconds for filename
        start_ms = int(start_sample / sample_rate * 1000)
        end_ms = int(end_sample / sample_rate * 1000)

        chunks_info.append({
            'start_sample': start_sample,
            'end_sample': end_sample,
            'start_ms': start_ms,
            'end_ms': end_ms
        })

    # Sort chunks by start time for consistency
    chunks_info.sort(key=lambda x: x['start_sample'])

    print(f"Fixed overlapping chunks. Original: {len(original_chunks)}, New: {len(chunks_info)}")
    return chunks_info


def main():
    parser = argparse.ArgumentParser(description='Extract random chunks from audio files')
    parser.add_argument('--csv', required=True, help='Input CSV file with audio filenames')
    parser.add_argument('--source', required=True, help='Source folder containing audio files')
    parser.add_argument('--dest', required=True, help='Destination folder for chunks')
    parser.add_argument('--chunks', type=int, default=15, help='Number of chunks to extract')
    parser.add_argument('--duration', type=int, default=120, help='Duration of each chunk in seconds')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible results (default: 42)')
    args = parser.parse_args()

    # Create destination folder if it doesn't exist
    os.makedirs(args.dest, exist_ok=True)

    # Read CSV file
    df = pd.read_csv(args.csv)

    for _, row in df.iterrows():
        input_file = Path(args.source) / row['recording_filename']
        if not input_file.exists():
            print(f"Warning: File not found: {input_file}")
            continue

        print(f"Processing: {input_file}")

        # Extract chunks
        chunks_info = extract_random_chunks(
            str(input_file),
            num_chunks=args.chunks,
            chunk_duration=args.duration,
            seed=args.seed
        )

        # Read audio file once
        audio_data, sample_rate = sf.read(str(input_file))

        # Save chunks
        for chunk in chunks_info:
            chunk_data = audio_data[chunk['start_sample']:chunk['end_sample']]
            output_filename = f"{input_file.stem}_{chunk['start_ms']}_{chunk['end_ms']}.wav"
            output_path = Path(args.dest) / output_filename

            sf.write(str(output_path), chunk_data, sample_rate)
            print(f"Created: {output_filename}")


if __name__ == "__main__":
    main()