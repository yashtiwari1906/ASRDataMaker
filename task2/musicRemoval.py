import argparse
import numpy as np 
import librosa 
from scipy.io.wavfile import write
import os 


def remove_music_save_audio(audio_path, output_path):
    audio_array, sample_rate = librosa.load(audio_path, sr=None)

    start_time, end_time = 11, None #start time is fix for 11 second audio 

    for i in range(len(audio_array) - sample_rate * 50, len(audio_array)):
        if np.mean(np.abs(audio_array[i:i+sample_rate])) > 0.1:  
            end_time = librosa.samples_to_time(i, sr=sample_rate)
            break

    if end_time is None:
        print(f"No Music found in the last for the audio at {audio_path}.")
        end_time = len(audio_array) - 1

    start_samples = librosa.time_to_samples(start_time, sr=sample_rate)
    end_samples = librosa.time_to_samples(end_time, sr=sample_rate)
    clipped_audio = audio_array[start_samples:end_samples]

    write(output_path, sample_rate, clipped_audio)
    print(f"audio at {audio_path} processed successfully!")

def process_audios(audio_folder_path, processed_audio_folder):
    os.makedirs(processed_audio_folder, exist_ok=True)
    for root, dirs, files in os.walk(audio_folder_path):
        for file in files:
            file_name = file.split(".")[0]
            if file.endswith(".wav") or file.endswith(".mp3"):
                audio_file_path, output_file_path = os.path.join(root, file), processed_audio_folder + file_name + ".wav"
                remove_music_save_audio(audio_file_path, output_file_path)

    print(f"Audio got processed successfully!")

if __name__ == "__main__":
    audio_folder_path, processed_audio_folder = "task2/parallel_processed_audios/", "task2/super_cleaned_audios/"
    parser = argparse.ArgumentParser(description='Provide audio folder path & processed_audio_folder path for storing processed audio ')
    parser.add_argument('-afp', '--audio_folder_path', type=str, required=True, default = audio_folder_path, help='provide the path where you have .wav or .mp3 files for which you want super clean audio (-afp or --audio_folder_path)')
    parser.add_argument('-pfp', '--processed_audio_folder', type=str, required=False, default = processed_audio_folder, help='provide the path where you want to store these processed super clean audio (-pfp or --processed_audio_folder) (not necessary if not provided it will be stored in processed_audio_folder)')
    
    args = parser.parse_args()
    audio_folder_path = args.audio_folder_path
    processed_audio_folder = args.processed_audio_folder

    if not os.path.exists(audio_folder_path):
        raise FileNotFoundError(f"folder path {audio_folder_path} doesn't exisits")

    process_audios(audio_folder_path, processed_audio_folder)
