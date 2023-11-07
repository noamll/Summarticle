from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread
from summarization_model import sumArticle2

app = Flask(__name__)

# Define the Flask app.

# Create an endpoint for submitting summarization tasks.
@app.route('/submit_summary', methods=['POST'])
def submit_summary_task():
    data = request.get_json()  # JSON data with the text to summarize.
    
    
    # Call the summarization function from your summarization model code.
    summary = sumArticle2(data['pdf_path'])

    return jsonify({'message': 'Summary task submitted successfully', 'summary' : summary})

# Set up a task queue and worker thread for summarization.
summary_queue = Queue()

def summary_worker():
    while True:
        task_data = summary_queue.get()
        # Process the summarization task using your logic.
        # You can call your summarization function here.
        # Task handling logic for summarization goes here.
        print("Summarizing:", task_data)
        summary_queue.task_done()

summary_worker_thread = Thread(target=summary_worker)
summary_worker_thread.daemon = True
summary_worker_thread.start()

# Create an endpoint for submitting translation tasks.
@app.route('/submit_translation', methods=['POST'])
def submit_translation_task():
    data = request.get_json()  # JSON data with the text to translate and target language.
    
    # Enqueue the translation task.
    translation_queue.put(data)  # Assuming 'data' contains the text and target language.

    return jsonify({'message': 'Translation task submitted successfully'})

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

# Run the Flask app.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)

