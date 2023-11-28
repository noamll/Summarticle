
#Here's a basic unit test for the get_summary endpoint using the unittest and flask_testing modules in Python. 
#This test checks if the endpoint returns a 200 status code when a valid paper_id is provided.

import unittest
from flask_testing import TestCase
from your_flask_app import app  # replace with your actual Flask app import

class TestGetSummary(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_get_summary(self):
        # Assuming '1234' is a valid paper_id in your uploaded_papers dictionary
        response = self.client.get('/get_summary/1234')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
