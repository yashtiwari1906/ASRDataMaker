import argparse
import soundfile as sf
import os 
import json 
import numpy # add in requirements

def get_audio_meta_data(audio_path):
    audio_array, sample_rate = sf.read(audio_path, dtype='float64')

    duration = round(len(audio_array)/sample_rate, 4) 

    #only duration for now 
    return duration 


def get_trancripts(transcript_path):

    with open(transcript_path, "r") as file:
        transcript = file.read() 

    return transcript

def single_audio_text_meta_data_json(audio_folder_path, transcript_folder_path, lesson):
    audio_path, transcript_path = audio_folder_path + lesson + ".wav", transcript_folder_path + lesson + ".txt" 
    if not os.path.exists(audio_path):
        print(FileNotFoundError(f"audio file {audio_path} don't exists not including in train mainfest jsonl"))
        return {}
    
    if not os.path.exists(transcript_path):
        print(FileNotFoundError(f"transcripts file {transcript_path} don't exists not including in train mainfest jsonl"))
        return {}

    duration =  get_audio_meta_data(audio_path)
    transcript = get_trancripts(transcript_path)

    single_train_example = {

        "audio_filepath": audio_path,
        "duration": duration,
        "text": transcript

    }

    return single_train_example


def make_manifest_file(audio_folder_path, transcript_folder_path, manifest_file_folder_path = "task4/"):
    manifest_list = [] 

    for root, dirs, files in os.walk(audio_folder_path):
        for file in files:
            audio_path = os.path.join(root, file)
            lesson = audio_path.split("/")[-1].split(".")[0]
            transcript_path = transcript_folder_path+lesson + ".txt"

            if file.endswith(".wav") and os.path.exists(transcript_path):
                single_train_example = single_audio_text_meta_data_json(audio_folder_path, transcript_folder_path, lesson)
                if single_train_example != {}:
                    manifest_list.append(single_train_example)

            elif not file.endswith(".wav"):
                print(f"data type other then .wav is observed in audio_folder {audio_path}")
            else:
                print(f"corresponding text file was not present for the lesson: {lesson} at path: {transcript_path}")

    save_manifest_file(manifest_file_folder_path, manifest_list)

    print(f"manifest file prepared successfully!")

def save_manifest_file(folder_path, manifest_list):
    os.makedirs(folder_path, exist_ok=True)
    mainfest_file_path = folder_path + "train_manifest.jsonl"
    with open(mainfest_file_path, "w") as file:
        for json_obj in manifest_list:
            json.dump(json_obj, file)
            file.write('\n')  

    print(f"Manifest file prepared successfully at {mainfest_file_path}")

if __name__ == "__main__":
    audio_folder_path, transcript_folder_path = "task2/super_cleaned_audios/", "task3/text_transcripts/"
    parser = argparse.ArgumentParser(description='Provide folder path for audio and transcripts')
    parser.add_argument('-afp', '--audio_folder_path', type=str, required=False, default = audio_folder_path, help='provide path for folder where cleaned audio files are there (-afp, --audio_folder_path)')
    parser.add_argument('-tfp', '--transcript_folder_path', type=str, required=False, default = transcript_folder_path, help='provide path for cleaned text transcripts (-tfp, --transcript_folder_path)')
    args = parser.parse_args()
    audio_folder_path = args.audio_folder_path
    transcript_folder_path = args.transcript_folder_path
    make_manifest_file(audio_folder_path, transcript_folder_path)