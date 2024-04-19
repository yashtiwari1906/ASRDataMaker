
from email.policy import default
import re
import os
from xml.dom import ValidationErr
import yt_dlp
import requests
import json 
import argparse
# import PyPDF2
# import fitz


def get_download_page_json(courseId = "106106184"):

    url = f"https://tools.nptel.ac.in/npteldata/downloads.php?id={courseId}"

    payload = {}
    headers = {}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
    except Exception as e:
        #In case any connection error abort the script
        print(f"response not fetched properly got an error check the internet connection once {e}")
        raise ConnectionError(e)

    if response.status_code != 200:
        raise ValidationErr(f"response not fetched properly error check the cURL once for url: {url}, {response}")

    return response.json()

def get_pdf_download_links(page_json):
    pdf_drive_link_dict = {}

    transcripts = page_json['data']['transcripts']
    for transcript in transcripts:
        downloads = transcript['downloads']
        for download in downloads:
            if download['language'] == "english-Verified":
                pdf_drive_link_dict[transcript['lesson_id']] = download['url']

    return pdf_drive_link_dict

def download_single_pdf(pdf_drive_link, file_path):

    #pdfId
    pdfId = pdf_drive_link.split("/")[-2]

    pdf_url = f"https://drive.google.com/uc?export=download&id={pdfId}"

    response = requests.get(pdf_url)

    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        print(f"PDF downloaded successfully at {file_path}.")
    else:
        print(f"Failed to download PDF at {file_path}. Status code:", response.status_code)


def download_transcript_pdfs(pdf_drive_link_dict, pdf_base_path):
    os.makedirs(pdf_base_path, exist_ok=True)
   
    for lessonId, pdf_drive_link in pdf_drive_link_dict.items():
        file_path = pdf_base_path+"lesson"+str(lessonId) + ".pdf"
        download_single_pdf(pdf_drive_link, file_path)

    print("Download complete!")

def filter_dictionary(pdf_drive_link_dict, num_pdfs):
    count = 0 
    filtered_dictionary = {}
    for key, value in pdf_drive_link_dict.items():
        if count == num_pdfs:
            break 
        filtered_dictionary[key] = value 
        count += 1
    
    return filtered_dictionary

def main(webpage_url, num_pdfs = 1000):
    PDF_BASE_PATH = "task1/pdf_transcripts/"
    courseId = webpage_url.split("/")[-1].strip("/")
    page_json = get_download_page_json(courseId=courseId)
    pdf_drive_link_dict = get_pdf_download_links(page_json)
    filtered_pdf_drive_link_dict = filter_dictionary(pdf_drive_link_dict, num_pdfs)
    download_transcript_pdfs(filtered_pdf_drive_link_dict, PDF_BASE_PATH) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide course URL for downloading pdfs')
    default_course_url = "https://nptel.ac.in/courses/106106184"
    parser.add_argument('-cu', '--course_url', type=str, required=False, default = default_course_url, help='provide the course URL for which you want to downnload the transcript (-cu or --course_url)')
    parser.add_argument('-n', '--num_sample', type=int, required=False, default = 1000, help='provide the number of audio data points you want to download (-n or --num_sample)')
    
    args = parser.parse_args()
    webpage_url = args.course_url
    num_sample = args.num_sample

    main(webpage_url, num_pdfs=num_sample)



