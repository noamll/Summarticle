from flask import Flask, request, jsonify
from AWS_SQS_Summarticle.py import send_message_to_queue, process_messages_from_queue

app = Flask(__name__)

# Expose an API endpoint for PDF upload
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['pdf']
        # Save the file or process its content as needed
        # For simplicity, assume the file is saved to a directory
        pdf_file.save('uploads/' + pdf_file.filename)

        # Send the file path to the orchestrator
        send_message_to_queue('uploads/' + pdf_file.filename)

        return jsonify({'message': 'PDF uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
