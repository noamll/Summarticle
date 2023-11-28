import boto3
import os
from pypdf import PdfReader
from transformers import AutoModelForSeq2SeqLM
from pypdf.errors import PdfReadError
from transformers import pipeline
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pyodbc
import json
import random

os.environ['AWS_DEFAULT_REGION'] = 'eu-north-1'

# Create an SQS client
sqs = boto3.client('sqs')

# Define the SQS queue URL
sqs_queue_url = 'https://sqs.eu-north-1.amazonaws.com/951932431518/Summarticle.fifo'


# ---- AI MODEL ---- 

def pdfTE(pdfFile, version=1, start=0, end=0):
    # Function for text extraction from PDF.
    # Version states which version to use, with arguments(start, end) being the starting page and ending page.
    if version == 1:
        with open(pdfFile, "rb") as file:
            pdfReader = PdfReader(file)
            for page in pdfReader.pages:
                yield page.extract_text()
    else:
        with open(pdfFile, "rb") as file:
            pdfReader = PdfReader(file)
            if end == 0:
                end = len(pdfReader.pages) - 1
            for num in range(start, end):
                yield pdfReader.pages[num].extract_text()


def articleC(pdfFile, version=1, start=0, end=0):
    # Function to return the article in one string.
    # Version and start, end arguments necessary for pdfTE integration.
    if version == 1:
        textCombiner = pdfTE(pdfFile)
    else:
        textCombiner = pdfTE(pdfFile, 2, start, end)
    textCombined = ""
    for text in textCombiner:
        textCombined += text
    if textCombined == "":
        raise Exception("Oops! The task failed as the PDF file is empty.")
    elif len(textCombined) < 10:
        raise Exception("Oops! The task failed as the PDF file has too few characters.")
    else:
        return textCombined




def sumArticle2(pdfFile, translate_summary=False):
    if pdfFile.endswith(".pdf"):
        try:
            summarizer = pipeline("summarization", model="pszemraj/led-large-book-summary")
            articleCombined = articleC(pdfFile)
            summarizedPage = summarizer(articleCombined, max_length=1000, min_length=200, do_sample=True)

            if translate_summary:
                # If translation is requested, translate the summary
                translated_text = translate_text(summarizedPage[0]["summary_text"])
                return translated_text
            else:
                # Otherwise, return the original English summary
                return summarizedPage[0]["summary_text"]

        except PdfReadError as PRE:
            return f"Oops! a PDF Read Error {PRE} happened. Please retry the task once the issue has been resolved."
        except OSError as OS:
            return f"Oops! an OS Error {OS} happened. Please retry the task once the issue has been resolved."
        except (RuntimeError, IndexError) as RIE:
            print(f"Oops! {RIE}, The file was too big to configure.")
            try:
                amountPages = int(input("Per how many pages would you like a summary? "))
                print("Warning, this summary may take a while to be produced.")
                if amountPages == 1:
                    end = amountPages
                else:
                    end = amountPages - 1
                start = 0
                summary = ""
                while end < len(PdfReader(ArticleToSummarize).pages):
                    articleCombined = articleC(pdfFile, 2, start, end)
                    if amountPages == 1:
                        summarizedPage = summarizer(articleCombined, max_length=200, min_length=50, do_sample=False)
                    else:
                        summarizedPage = summarizer(articleCombined, max_length=1000, min_length=200, do_sample=False)
                    summary += f"Summary of pages {start + 1}-{end + 1}\n" + summarizedPage[0]["summary_text"] + '\n'
                    start += amountPages
                    end += amountPages
                return summary
            except ValueError as VE:
                return f"Oops! {VE}, You didn't give an integer."
            except IndexError as IE:
                return f"Oops! {IE}, you gave an integer larger than the actual number of pages in the paper."
            except Exception as E:
                return f"Oops! An unexpected error occurred, {E}. Please report the error to the team."
    else:
        raise Exception("The file format is not a valid pdf.")




def pdfKE(pdfFile, language='english'):
    # Function to extract keywords from the PDF.
    # Language input needed as the language needs to be part of the stopwords folder. Standard keyword is English.
    if pdfFile.endswith(".pdf"):
        try:
            articleCombined = articleC(pdfFile).lower()
            tokens = word_tokenize(articleCombined)
            punctuations = ["(", ")", ";", ":", "[", "]", ",", "!", "=", "==", "<", ">", "@", "#", "$", "%", "^", "&",
                            "*", ".", "//", "{", "}", "...", "``", "+", "''", "-", "~", "\"", '’']
            stopWords = stopwords.words(f'{language}')
            keywords = [word for word in tokens if word not in stopWords and word not in punctuations]
            keywordExtracted = pd.Series(keywords).value_counts().index[:5]
            keywordDict = {i + 1: keywordExtracted[i] for i in range(5)}
            return keywordDict
        except PdfReadError as PRE:
            return f"Oops! a PDF Read Error {PRE} happened. Please retry the task once the issue has been resolved."
        except OSError as OS:
            return f"Oops! an OS Error {OS} happened. Please retry the task once the issue has been resolved."
    else:
        return f"Oops! The task failed. Please retry the task once the issue has been resolved."

# Summarization translation
translation_model = pipeline("translation", model="Helsinki-NLP/opus-mt-en-nl")  # Create translation pipeline

def translate_text(text):
    translation_result = translation_model(text)
    return translation_result[0]['translation_text']


# ---- END AI MODEL ---- 

# ---- JSON to DB ---- 

#Database functions
import pyodbc
import json
import random

# Replace 'your_connection_string' with your actual connection string
connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=Summarticle_database.accdb;'

def save_paper(json_data):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    paper_title = json_data.get("paper", {}).get("title")
    
    # Check if the paper title is not already in the Paper table
    select_query = "SELECT * FROM papers WHERE title = ?"
    cursor.execute(select_query, (paper_title,))
    
    if not cursor.fetchone():
        # Paper title is not in the Paper table, save the paper
        insert_query = "INSERT INTO papers (title, authors, DOI, keywords) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (
            paper_title,
            json_data.get("paper", {}).get("authors"),
            json_data.get("paper", {}).get("DOI"),
            ', '.join(json_data.get("paper", {}).get("keywords", []))
        ))
        
        connection.commit()

    cursor.close()
    connection.close()

def save_summary(json_data):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    paper_title = json_data.get("summary", {}).get("title")
    
    # Check if the paper title is not already in the Summary table
    select_query = "SELECT * FROM summary WHERE title = ?"
    cursor.execute(select_query, (paper_title,))
    
    if not cursor.fetchone():
        # Paper title is not in the Summary table, save the summary
        insert_query = "INSERT INTO summary (title, summary_en, rating_en) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (
            paper_title,
            json_data.get("summary", {}).get("summary_en"),
            json_data.get("summary", {}).get("rating_en", 0)
        ))
        
        connection.commit()
    else:
        # Paper title is already in the Summary table, save summary in a new row
        insert_query = "INSERT INTO summary (title, summary_en, rating_en) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (
            paper_title,
            json_data.get("summary", {}).get("summary_en"),
            json_data.get("summary", {}).get("rating_en", 0)
        ))

        connection.commit()

    cursor.close()
    connection.close()

def read_summary(json_data):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    paper_title = json_data.get("title")
    language = json_data.get("language", "en")

    # Check whether JSON GET request is from summary_en or summary_nl
    if language == "en":
        select_query = "SELECT summary_en, rating_en FROM summary WHERE title = ? AND summary_en IS NOT NULL"
    elif language == "nl":
        select_query = "SELECT summary_nl, rating_nl FROM summary WHERE title = ? AND summary_nl IS NOT NULL"
    else:
        return None  # Invalid language
    
    cursor.execute(select_query, (paper_title,))
    result = cursor.fetchone()

    if result:
        # If there is a summary in the requested language, return it based on the rating
        summary, rating = result
        return summary if random.random() < rating / 10.0 else None  # Weighted random based on rating
    else:
        return None  # Create a new summary (you already have code for this)

    cursor.close()
    connection.close()

def read_keyword(text):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    keyword = text

    # Get keyword from JSON request
    select_query = "SELECT title FROM papers WHERE keywords LIKE ?"
    cursor.execute(select_query, ('%' + keyword + '%',))
    result = cursor.fetchall()

    if result:
        # If there are papers with the specified keyword, return the titles
        return [row[0] for row in result]
    else:
        return None

    cursor.close()
    connection.close()

def update_rating(json_data):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    paper_title = json_data.get("title")
    rating_type = json_data.get("rating_type")

    # If JSON-rating == thumbs-up, corresponding rating in table += 1
    # If JSON-rating == thumbs-down, corresponding rating in table -= 1
    if rating_type == "thumbs-up":
        update_query = "UPDATE summary SET rating_en = CASE WHEN rating_en + 1 > 10 THEN 10 ELSE rating_en + 1 END WHERE title = ?"
    elif rating_type == "thumbs-down":
        update_query = "UPDATE summary SET rating_en = CASE WHEN rating_en - 1 < 1 THEN 1 ELSE rating_en - 1 END WHERE title = ?"
    else:
        return None  # Invalid rating type

    cursor.execute(update_query, (paper_title,))
    connection.commit()

    cursor.close()
    connection.close()

def delete_summary():
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    # If summary_rating is lower than 3, delete from Summary table
    delete_query = "DELETE FROM summary WHERE rating_en < 3"
    cursor.execute(delete_query)
    connection.commit()

    cursor.close()
    connection.close()
    
# ---- END JSON to DB ---- 

# QUEUE

def send_message_to_queue(pdf_file_path, translate_summary=False):
    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=pdf_file_path,
        MessageGroupId='group1',
        MessageAttributes={
            'TranslateSummary': {
                'DataType': 'String',
                'StringValue': str(translate_summary)
            }
        }
    )
    return response



# Process messages from the SQS queue
def process_messages_from_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=sqs_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=300  # Set a visibility timeout (in seconds)
        )
        if 'Messages' in response:
            message = response['Messages'][0]
            body = message['Body']
            receipt_handle = message['ReceiptHandle']

            try:
                # Check if translation is requested
                translate_summary = message.get('TranslateSummary', '').lower() == 'true'

                # Perform summarization
                summary = sumArticle2(body, translate_summary)

                # Print or use the summary
                print(summary)

            finally:
                # Delete the message from the queue
                sqs.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=receipt_handle
                )
        else:
            break


# Example usage:
# Send a message to the SQS queue
#send_message_to_queue('C:\\Users\\arash\\Downloads\\Bilingualism and the role of music in early language acquisition_ u719136.pdf')

# Process messages from the SQS queue
process_messages_from_queue()
