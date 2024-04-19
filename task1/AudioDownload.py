import re
import os
from xml.dom import ValidationErr
import yt_dlp
import requests
import json 
import argparse 


def get_course_page_json(courseId = "106106184"):

    url = f"https://tools.nptel.ac.in/npteldata/course_outline1.php?id={courseId}"

    payload = {}
    headers = {}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        print(f"response not fetched properly got an error check internet connection once or url {e}")
        raise ConnectionError(e)

    if response.status_code != 200:
        raise ValidationErr(f"response not fetched properly error check the cURL once for url: {url}, {response}")
    return response.json()

def get_youtube_ids_dict_list(page_response_json):

    res_youtube_ids_dict_list = [] 

    course_units = page_response_json['data']['units']
    for week in course_units:
        lessons = week['lessons']
        for lesson in lessons:
            youtubeId = lesson['youtube_id']
            lessonId = lesson['id']
            res_youtube_ids_dict_list.append({"lessonId": lessonId, "youtubeId":youtubeId})

    return res_youtube_ids_dict_list


def download_single_youtube_audio(file_name, url):
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': file_name + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    } 
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"audio for lesson: {file_name} and youtube video {url} downloaded successfully")
        
    except Exception as e:
        print(f"some error happend and download for {url} was not correctly happened or not happened at all, due to {e}")

    

# Function to download audio from YouTube videos using yt-dlp
def download_audio_from_youtube(id_url_dict_list, output_dir):
    
    os.makedirs(output_dir, exist_ok=True)

    for id_url_dict in id_url_dict_list:
        file_name, url = "lesson"+str(id_url_dict['lessonId']), id_url_dict['url']
        download_single_youtube_audio(output_dir+file_name, url)
    

def get_youtube_url_lessonId_dicts(youtubeIds_dict_list):
    
    youtube_ids_urls = []

    for youtube_dict in youtubeIds_dict_list:
        lessonId, youtubeId = youtube_dict['lessonId'], youtube_dict['youtubeId']
        URL = f"https://www.youtube.com/watch?v={youtubeId}&t=1s" 
        youtube_ids_urls.append({"lessonId": lessonId, "url":URL})
    
    return youtube_ids_urls


# Main function to download audio from all YouTube videos on a webpage
def download_audios_from_ids(youtubeIds_dict_list, output_dir = "./task1/Audios"):
    youtube_ids_urls = get_youtube_url_lessonId_dicts(youtubeIds_dict_list)
    download_audio_from_youtube(youtube_ids_urls, output_dir)

def main(webpage_url, num_audios = 1000):
    output_dir = "./task1/Audios/"
    courseId = webpage_url.split("/")[-1].strip("/")
    page_response_json = get_course_page_json(courseId=courseId)
    youtubeIds_dict_list = get_youtube_ids_dict_list(page_response_json)
    limited_youtubeIds_dict_list = youtubeIds_dict_list[:num_audios]
    download_audios_from_ids(limited_youtubeIds_dict_list, output_dir) 
# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide course URL for downloading Audios')
    default_course_url = "https://nptel.ac.in/courses/106106184"
    parser.add_argument('-cu', '--course_url', type=str, required=False, default = default_course_url, help='provide the course URL for which you want to downnload the Audios (-cu or --course_url)')
    parser.add_argument('-n', '--num_sample', type=int, required=False, default = 1000, help='provide the number of audio data points you want to download (-n or --num_sample)')

    args = parser.parse_args()

    webpage_url = args.course_url
    num_sample = args.num_sample
    main(webpage_url, num_audios=num_sample)
    
