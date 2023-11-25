import boto3
import os
from pypdf import PdfReader
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM
from pypdf.errors import PdfReadError

os.environ['AWS_DEFAULT_REGION'] = 'eu-north-1'


# Create an SQS client
sqs = boto3.client('sqs')

# Define the SQS queue URL
sqs_queue_url = 'https://sqs.eu-north-1.amazonaws.com/951932431518/Summarticle.fifo'

# Define the summarizer function
def sumArticle1(pdfFile): # Function to summarize article per page
    if pdfFile.endswith(".pdf"):
        try:
            print("Start Summarizing")
            summarizer = AutoModelForSeq2SeqLM.from_pretrained("pszemraj/led-large-book-summary") # Model used from the huggingface hub (https://huggingface.co/pszemraj/led-large-book-summary)
            for text in pdfTE(pdfFile): # Iterate over generator
                summarizedPage = summarizer(text)
                print(summarizedPage, end="\n")
                print()
        except PdfReadError:
            return 0
        except OSError:
            return 0
        
def sumArticle2(pdfFile):
    if pdfFile.endswith(".pdf"):
        try:
            print('Start Summarizing')
            summarizer = AutoModelForSeq2SeqLM.from_pretrained("pszemraj/led-large-book-summary")
            articleCombined = articleC(pdfFile)
            summarizedPage = summarizer(articleCombined)
            summarizedPage = summarizer(articleCombined)
        except PdfReadError:
            return 0
        except OSError:
            return 0
    else:
        return 0

# Translation function using transformers pipeline.
def translate_text(text, target_language):
    translation_pipeline = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-nl")
    translation_result = translation_pipeline(text, target_lang=target_language)
    return translation_result[0]['translation_text']

# Send messages to the SQS queue
def send_message_to_queue(message):
    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=message,
        MessageGroupId='group1'
    )
    return response

# Process messages from the SQS queue
def process_messages_from_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=sqs_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if 'Messages' in response:
            message = response['Messages'][0]
            body = message['Body']
            receipt_handle = message['ReceiptHandle']
            
            # Perform summarization
            summary = sumArticle2(body)
            
            # Perform translation
            translation = translate_text(summary, "nl")
            
            # Print the translated text
            print(translation)
            
            # Delete the message from the queue
            sqs.delete_message(
                QueueUrl=sqs_queue_url,
                ReceiptHandle=receipt_handle
            )
        else:
            break

# Example usage:
# Send a message to the SQS queue
# send_message_to_queue('C:\\Users\\arash\\Downloads\\Bilingualism and the role of music in early language acquisition_ u719136.pdf')

# Process messages from the SQS queue
process_messages_from_queue()

