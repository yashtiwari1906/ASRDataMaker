import argparse
from xml.dom import ValidationErr
import fitz
import os 
import sys 
import string 
from num2words import num2words
import re 
import json 

class TextProcessing:
    def __init__(self) -> None:
        self.name = "Text Preprocessor"
        self.ultra_fine_segments_info = {} 


    def remove_punctuation(self, text): 
        translation_table = str.maketrans('', '', string.punctuation + '\n\r')
        text = text.translate(translation_table)
        return text 

    def convert_num2words(self, text): 
        # Regular expression to find numbers in the text
        pattern = r'\b\d+\b'
        numbers = re.findall(pattern, text)
        for number in numbers:
            text_representation = num2words(int(number))
            text = text.replace(number, text_representation)

        return text

    def save_segments(self, text_list, time_info_text, lecture_name):
        """
        This fuction is to save the text segemnts specific to time period so that speech-text pair will be of small lengths which eventually helps
        in generalizing model to audio clips of different sizes 
        """
        refer_time = time_info_text.split()[-1].rstrip(")") 
        cleaned_txt = self.process(" ".join(text_list), lecture_name)  #used same process function to clean this segment of text 
        sub_text_dict = {str(refer_time): cleaned_txt} 
        if lecture_name in self.ultra_fine_segments_info:
            self.ultra_fine_segments_info[lecture_name].append(sub_text_dict)
        else:
            self.ultra_fine_segments_info[lecture_name] = [sub_text_dict]

    def save_ultra_fine_segment_dictionary(self, folder_path, lecture_name):
        
        with open(folder_path+lecture_name+".json", "w") as file:
            json.dump(self.ultra_fine_segments_info, file)

        print(f"json for {lecture_name} is saved")

    def advance_processing(self, text, lecture_name):
        """
        Three main tasks are going on here:
        1.) removing the meta-data in the pdf of Institute info, prof info etc
        2.) removing time segment reference 
        3.) saving ultra fine text segments wrt time mentioned in the text 
        
        """
        self.ultra_fine_segments_info = {} #reinitializing the dictionary to save all the elements as list in the key of leture name
        text_list = text.split("\n")
        idx = 0
        for i, txt in enumerate(text_list):
            if "lecture" in txt.lower():
                idx = i + 2  #ensuring not to include chapter or chapter introductory line below lecture
                break 
        
        text_list = text_list[idx:] 

        #taking out the 'refer slide time' statements 
        cleaned_text_list = [] 
        prevIdx = 0
        for i, txt in enumerate(text_list):
            if "refer" in txt.lower() and "slide" in txt.lower() and "time" in txt.lower():
                self.save_segments(text_list[prevIdx:i], txt, lecture_name) 
                prevIdx = i + 1
            else:
                cleaned_text_list.append(txt)

        #save last segment with the end time 
        self.save_segments(text_list[prevIdx:i], "end", lecture_name)

        return " ".join(cleaned_text_list) 

    def process(self, text, lecture_name, lower_case = True, remove_punctuation = True, convert_num2words = True, advance_processing = False):
        if lower_case:
            text = text.lower() 
        
        if advance_processing:
            text = self.advance_processing(text, lecture_name)

        if remove_punctuation:
            text = self.remove_punctuation(text)

        if convert_num2words:
            text = self.convert_num2words(text)

        return text 

class ConverterEngine:
    def __init__(self, pdf_folder_path, txt_folder_path, fine_detail_transcript_folder) -> None:
        self.pdf_folder_path = pdf_folder_path
        self.fine_detail_transcript_folder = fine_detail_transcript_folder
        self.txt_folder_path = txt_folder_path
        
        #creating directories if not exists
        os.makedirs(txt_folder_path, exist_ok=True) 
        os.makedirs(fine_detail_transcript_folder, exist_ok=True) 

        #text preprocessor
        self.text_preprocessor = TextProcessing()

    def extract_text(self, pdf_path, text_path, preprocess, advance_processing):
        text = ""
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()
        except Exception as e:
            print(ValidationErr(f"there was some problem in reading the pdf file follow the error: {e}"))
            return 

        if preprocess:
            lecture_name = text_path.split("/")[-1].split(".")[0]
            text =self.text_preprocessor.process(text = text, lecture_name = lecture_name, advance_processing = advance_processing)
            self.text_preprocessor.save_ultra_fine_segment_dictionary(self.fine_detail_transcript_folder, lecture_name)

        with open(text_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)
        
        print(f"converted pdf: {pdf_path} successfully to text and saved as {text_path}")


    def process_pdfs(self, preprocess = False, advance_processing = False):

        for root, dirs, files in os.walk(self.pdf_folder_path):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path, text_path = os.path.join(root, file),  self.txt_folder_path + file.split(".")[0] + ".txt"
                    self.extract_text(pdf_path, text_path, preprocess, advance_processing)


if __name__ == "__main__":
    pdf_folder_path, txt_folder_path, fine_detail_transcript_folder = "task1/pdf_transcripts/", "task3/text_transcripts/", "task3/transcripts_fine_details/"
    parser = argparse.ArgumentParser(description='provide paths for pdfs & where you want text files to be saved')
    parser.add_argument('-pfp', '--pdf_folder_path', type=str, required=False, default = pdf_folder_path, help='path to folder where pdf files are stored (-pfp or --pdf_folder_path)')
    parser.add_argument('-tfp', '--txt_folder_path', type=str, required=False, default = txt_folder_path, help='path to folder where you want text files to be stored (-tfp or --txt_folder_path)')

    args = parser.parse_args()
    pdf_folder_path = args.pdf_folder_path
    txt_folder_path = args.txt_folder_path

    converter = ConverterEngine(pdf_folder_path, txt_folder_path, fine_detail_transcript_folder)
    converter.process_pdfs(preprocess=True, advance_processing=True)
    print("Text extracted from PDF and saved to text document successfully.")
