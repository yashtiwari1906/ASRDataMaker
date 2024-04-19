"""
This file will run all the tasks all at once and store the results in their respective folders

"""
import argparse
from task1.audioDownload import main as audioDownloader
from task1.transcriptsDownload import main as pdfTranscriptDownloader
from task2.musicRemoval import process_audios as audioCleanser
from task3.pdf2text_converter import ConverterEngine 
from task4.prepareManifestFile import make_manifest_file 
import subprocess

def run_bash_script(bash_script_path, input1, input2, input3):
    subprocess.run(['bash', bash_script_path, input1, input2, input3])
    print(f"bash script ran successfully")

def cleanup(cleanup_bash_script_path):
    subprocess.run(['bash', cleanup_bash_script_path])
    print(f"all folders containing data related to *.wav, *.mp3, *.txt, *.pdf is flushed and will generate new data in some time!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide course URL for conquering ASR')
    default_course_url = "https://nptel.ac.in/courses/106106184"
    parser.add_argument('-cu', '--course_url', type=str, required=False, default = default_course_url, help='provide the course URL for which you want to downnload the Audios (-cu or --course_url)')
    parser.add_argument('-n', '--num_samples', type=int, required=False, default = 10, help='provide number of samples you want to download by default it is 10 (-n or --num_samples)')

    args = parser.parse_args()
    webpage_url = args.course_url
    num_samples = args.num_samples
    cleanup_bash_script_path = "cleanup.sh"
    #cleanup 
    cleanup(cleanup_bash_script_path)
    #task1
    audioDownloader(webpage_url, num_audios=num_samples)
    pdfTranscriptDownloader(webpage_url, num_pdfs=num_samples)
    print(f"audio & pdfs are downloaded successfully!")

    #task2
    run_bash_script("task2/audio_converter_parallel.sh", "./task1/Audios/", "task2/parallel_processed_audios", '6')
    audioCleanser(audio_folder_path="task2/parallel_processed_audios/", processed_audio_folder = "task2/super_cleaned_audios/")

    #task3
    converter = ConverterEngine( pdf_folder_path = "task1/pdf_transcripts/", txt_folder_path = "task3/text_transcripts/", fine_detail_transcript_folder = "task3/transcripts_fine_details/")
    converter.process_pdfs(preprocess=True, advance_processing=True)
    print("Text extracted from PDF and saved to text document successfully.")

    # #task4
    make_manifest_file(audio_folder_path = "task2/super_cleaned_audios/", transcript_folder_path = "task3/text_transcripts/")

    print("#"*40)
    print("Done and Dusted!!!!")
    print("#"*40)