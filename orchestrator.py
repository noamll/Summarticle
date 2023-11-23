from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread
from summarization_model import sumArticle2
from transformers import pipeline
import boto3
import json



sqs_queue_url = 'https://sqs.eu-north-1.amazonaws.com/951932431518/Summarticle.fifo'

# Create an SQS client
sqs = boto3.client('sqs')


app = Flask(__name__)



# Create an endpoint for submitting summarization tasks.
@app.route('/submit_summary', methods=['POST'])
def submit_summary_task():
    data = request.get_json()  # JSON data with the text to summarize.

    # Send message to SQS queue with the entire PDF content as the message body
    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=data['pdf_content'],  # Assuming 'pdf_content' is the key for the PDF content
        MessageGroupId='1'  # Specify the message group ID
    )

    return jsonify({'message': 'Summary task submitted successfully', 'summary': response['MessageId']})


def summary_worker():
    while True:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=sqs_queue_url,
            AttributeNames=['All'],
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        # Process the received message
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Process the message data safely using json.loads
            try:
                pdf_content = message['Body']
                summary = sumArticle2(pdf_content)

                # Add your logic for processing the summarized data
                print("Summarizing:", summary)
            except Exception as e:
                print(f"Error processing PDF content: {e}")

            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=sqs_queue_url,
                ReceiptHandle=receipt_handle
            )


# Create an endpoint for submitting translation tasks.
@app.route('/submit_translation', methods=['POST'])
def submit_translation_task():
    data = request.get_json()  # JSON data with the text to translate and target language.
    
    # Call the translation function.
    translation = translate_text(data['text'], data['target_language'])

    return jsonify({'message': 'Translation task submitted successfully', 'translation': translation})

# Set up a task queue and worker thread for translation.
translation_queue = Queue()

def translation_worker():
    while True:
        task_data = translation_queue.get()
        # Process the translation task using your logic.
        # You can call your translation function here.
        # Task handling logic for translation goes here.
        print("Translating:", task_data)
        translation_queue.task_done()

translation_worker_thread = Thread(target=translation_worker)
translation_worker_thread.daemon = True
translation_worker_thread.start()

# Create an endpoint for submitting recommended articles tasks.
@app.route('/submit_recommend', methods=['POST'])
def submit_recommend_task():
    data = request.get_json()  # JSON data with information to generate recommendations.
    
    # Enqueue the recommended articles task.
    recommend_queue.put(data)  # Assuming 'data' contains relevant information.

    return jsonify({'message': 'Recommendation task submitted successfully'})

# Set up a task queue and worker thread for recommended articles.
recommend_queue = Queue()

def recommend_worker():
    while True:
        task_data = recommend_queue.get()
        # Process the recommended articles task using your logic.
        # Task handling logic for recommendations goes here.
        print("Generating recommendations:", task_data)
        recommend_queue.task_done()

recommend_worker_thread = Thread(target=recommend_worker)
recommend_worker_thread.daemon = True
recommend_worker_thread.start()

# Translation function using transformers pipeline.
def translate_text(text, target_language):
    translation_pipeline = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-nl")
    translation_result = translation_pipeline(text, target_lang=target_language)
    return translation_result[0]['translation_text']

# Run the Flask app.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
