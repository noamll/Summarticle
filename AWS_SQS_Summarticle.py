import boto3
import os
from pypdf import PdfReader
from transformers import AutoModelForSeq2SeqLM
from pypdf.errors import PdfReadError
from transformers import pipeline
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

os.environ['AWS_DEFAULT_REGION'] = 'eu-north-1'

# Create an SQS client
sqs = boto3.client('sqs')

# Define the SQS queue URL
sqs_queue_url = 'https://sqs.eu-north-1.amazonaws.com/951932431518/Summarticle.fifo'


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
