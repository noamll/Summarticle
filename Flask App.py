# For Flask app
from flask import Flask, request, jsonify

# For AWS SQS
from AWS_SQS_Summarticle import send_message_to_queue, process_messages_from_queue
import time
import uuid

# For JSON to DB
from AWS_SQS_Summarticle import save_summary
from AWS_SQS_Summarticle import read_summary
from AWS_SQS_Summarticle import read_keyword
from AWS_SQS_Summarticle import update_rating
from AWS_SQS_Summarticle import delete_summary
from AWS_SQS_Summarticle import save_paper
from AWS_SQS_Summarticle import translate_text


# Create Flask app
app = Flask(__name__)


# Create a dictionary to store uploaded papers and their IDs
uploaded_papers = {}

# Expose an API endpoint for PDF upload:
# It's extracting the file from the request using request.files['paper'].
# It's extracting the translate_summary flag from the request. If the flag is not provided, it defaults to False.
# It's generating a unique ID for the paper using uuid.uuid4().
# It's saving the file to a directory named 'uploads'.
# It's storing the file path, the translate_summary flag, and the paper ID in the uploaded_papers dictionary.
# It's sending the paper ID back to the client in the response.

@app.route('/upload-article', methods=['POST'])
def upload_pdf():
    try:
        pdf_file = request.files['paper']
        translate_summary = request.form.get('translate_summary', '').lower() == 'true'
        
        # Generate a unique paper ID
        paper_id = str(uuid.uuid4())

        
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



# New endpoint for saving summaries to the database:
# It's extracting the JSON data from the request using request.get_json(). 
# This data is expected to contain the summary and possibly a translate_summary flag.
# It's checking if the translate_summary flag is present and set to True in the JSON data. If the flag is not provided, it defaults to False.
# If translation is requested, it's translating the summary using the translate_text function. 
# It's then saving the translated summary to the database using the save_summary function. 
# The save_summary function is called with a new dictionary containing the title from the original JSON data and the translated summary.
# Regardless of whether translation was requested, it's saving the original summary to the database using the save_summary function. 
# The save_summary function is called with the original JSON data.

@app.route('/save-summary', methods=['POST'])
def save_translated_summary():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Check if translation is requested
        if json_data.get('translate_summary', False):
            # Translate the summary
            translated_summary = translate_text(json_data['summary'])  

            # Save the translated summary to the database
            save_summary({'title': json_data['title'], 'summary': translated_summary})

        # Save the original summary to the database
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

            # If summary is not None, return the summary
            if summary is not None:
                return jsonify({'summary': summary}), 200
            else:
                # If there is no summary for this article, summarize it using the AI model
                text = sumArticle2(paper_title) #Generate the summary

                # Save the paper and the summary
                save_paper(json_data) #save the paper 
                save_summary(json_data) # Save the summary

                # Return the new summary
                return jsonify({'summary': text}), 200
        else:
            return jsonify({'error': 'Invalid paper ID'}), 400
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500
        

#In this code, the read_keyword_endpoint function gets the keyword from the JSON data in the request, 
#calls the read_keyword function to get the titles of the papers that contain the keyword, and returns the titles.
@app.route('/read-keyword', methods=['POST'])
def read_keyword_endpoint():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Get the keyword from the JSON data
        keyword = json_data.get('keyword')

        # Call the read_keyword function and get the titles
        titles = read_keyword(keyword)

        # Return the titles
        return jsonify({'titles': titles}), 200
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500


#The update_rating_endpoint function gets the JSON data from the request and calls the update_rating function to update the rating of the summary. 
#It then returns a success message.
@app.route('/update-rating', methods=['POST'])
def update_rating_endpoint():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Update the rating
        update_rating(json_data)

        # Return a success message
        return jsonify({'message': 'Rating updated successfully'}), 200
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500


#The delete_summary_endpoint function calls the delete_summary function to delete the summary with a rating lower than 3. 
#It then returns a success message.
@app.route('/delete-summary', methods=['DELETE'])
def delete_summary_endpoint():
    try:
        # Delete the summary
        delete_summary()

        # Return a success message
        return jsonify({'message': 'Summary deleted successfully'}), 200
    except Exception as e:
        # Return an error message in case of exceptions
        return jsonify({'error': str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)


