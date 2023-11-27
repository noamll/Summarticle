from flask import Flask, request, jsonify
from AWS_SQS_Summarticle import send_message_to_queue, process_messages_from_queue
import time


app = Flask(__name__)

# Expose an API endpoint for PDF upload
@app.route('/upload-article', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['paper']
        translate_summary = request.form.get('translate_summary', '').lower() == 'true'
        
        # Save the file or process its content as needed
        # For simplicity, assume the file is saved to a directory
        pdf_file.save('uploads/' + pdf_file.filename)

        # Send the file path and translation flag to the orchestrator
        send_message_to_queue('uploads/' + pdf_file.filename, translate_summary)

        return jsonify({'message': 'PDF uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New route to handle GET request for a summary
@app.route('/get_summary/<int:id>', methods=['GET'])
def get_summary(id):
    try:
        # Simulate processing time for the summary
        time.sleep(5)

        # Retrieve the summary from the orchestrator
        summary = process_messages_from_queue(id)

        # Return summary data as JSON
        return jsonify({'summary': summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
