import unittest
import json
from flask import Flask
from werkzeug.datastructures import FileStorage
from orchestrator import app 
import time

class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_upload_pdf(self):
        with open('Bilingualism and the role of music in early language acquisition_ u719136.pdf', 'rb') as f:
            data = {
                'paper': (f, 'Bilingualism and the role of music in early language acquisition_ u719136.pdf'),
                'translate_summary': 'true'
            }
            response = self.client.post('/upload-article', content_type='multipart/form-data', data=data)
            
            print(response.data)  # Add this line
            paper_id = json.loads(response.data)['paper_id']

            # Simulate processing time
            time.sleep(5)

            response = self.client.get(f'/get_summary/{paper_id}')
            translate_summary = data['translate_summary'] == 'true'
            summary = json.loads(response.data)['summary']

            # Check if the summary is translated
            # This will depend on how you're implementing translation
            # For this example, let's assume that a translated summary always starts with '[Translated]'
            self.assertEqual(summary.startswith('[Translated]'), translate_summary)

if __name__ == '__main__':
    unittest.main()
