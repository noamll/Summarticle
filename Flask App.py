from flask import Flask, request, jsonify
from AWS_SQS_Summarticle import send_message_to_queue, process_messages_from_queue
from AWS_SQS_Summarticle import save_summary
from AWS_SQS_Summarticle import read_summary
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



#New endpoint for saving summaries to the database
@app.route('/save-summary', methods=['POST'])
def save_translated_summary():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Save the summary to the database
        save_summary(json_data)

        # Return a success message
        return jsonify({'message': 'Summary saved successfully'}), 200
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500


#new endpoint for retrieving a summary stored in the database, based on paper ID
@app.route('/get-summary/<string:paper_id>', methods=['GET'])
def get_summary(paper_id):
    try:
        # Check if the paper ID exists in the dictionary
        if paper_id in uploaded_papers:
            # Get the paper title from the uploaded_papers dictionary using the paper_id
            paper_title = uploaded_papers.get(paper_id, {}).get('file_path', '').split('/')[-1]

            # Create a JSON data structure with the paper title
            json_data = {'title': paper_title}

            # Retrieve the summary from the database
            summary = read_summary(json_data)

            # Return the summary
            return jsonify({'summary': summary}), 200
        else:
            return jsonify({'error': 'Invalid paper ID'}), 400
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)


