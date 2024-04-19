#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_folder> <output_folder> <num_cpus>"
    exit 1
fi

# Assign input and output folder paths
input_folder="$1"
output_folder="$2"
N="$3"

# Create the output folder if it doesn't exist
mkdir -p "$output_folder"

# Define the conversion function
convert_audio() {
    mp3_file="$1"
    filename=$(basename -- "$mp3_file")
    filename_no_ext="${filename%.*}"
    wav_file="$output_folder/$filename_no_ext.wav"
    ffmpeg -y -i "$mp3_file" -ac 1 -ar 16000 "$wav_file"
    echo "Converted $mp3_file to $wav_file"
}

# Loop through each MP3 file in the input folder and process in parallel
for mp3_file in "$input_folder"/*.mp3; do
    (convert_audio "$mp3_file") &
done

# Wait for all processes to finish
wait

echo "Conversion completed!"
