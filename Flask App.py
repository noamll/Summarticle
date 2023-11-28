from flask import Flask, request, jsonify
from AWS_SQS_Summarticle import send_message_to_queue, process_messages_from_queue
import time
import uuid


app = Flask(__name__)


# Create a dictionary to store uploaded papers and their IDs
uploaded_papers = {}

# Expose an API endpoint for PDF upload
@app.route('/upload-article', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['paper']
        translate_summary = request.form.get('translate_summary', '').lower() == 'true'
        
        # Generate a unique paper ID
        paper_id = str(uuid.uuid4())

        # Save the file or process its content as needed
        # For simplicity, assume the file is saved to a directory
        pdf_file.save('uploads/' + pdf_file.filename)

        # Store the file path, translation flag, and paper ID in the dictionary
        uploaded_papers[paper_id] = {
            'file_path': 'uploads/' + pdf_file.filename,
            'translate_summary': translate_summary
        }

        # Send the paper ID to the client
        return jsonify({'paper_id': paper_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New route to handle GET request for a summary
@app.route('/get_summary/<string:paper_id>', methods=['GET'])
def get_summary(paper_id):
    try:
        # Check if the paper ID exists in the dictionary
        if paper_id in uploaded_papers:
            # Simulate processing time for the summary
            time.sleep(5)

            # Retrieve the file path and translation flag from the dictionary
            file_path = uploaded_papers[paper_id]['file_path']
            translate_summary = uploaded_papers[paper_id]['translate_summary']

            # Process the file path and translation flag as needed
            summary = process_messages_from_queue(file_path, translate_summary)

            # Return summary data as JSON
            return jsonify({'summary': summary}), 200
        else:
            return jsonify({'error': 'Invalid paper ID'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)


