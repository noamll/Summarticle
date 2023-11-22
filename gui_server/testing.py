from fastapi.testclient import TestClient
import responses
import gui_server
import unittest



client = TestClient(gui_server.app)

class TestServer(unittest.TestCase):
    def setUp(self):
        self.r_mock = responses.RequestsMock(assert_all_requests_are_fired=True)
        self.r_mock.start()

    def tearDown(self):
        self.r_mock.stop()

    def test_normal_upload(self):
        self.r_mock.post(
            "http://ORCHESTRATOR/upload_article",
            json={
                "summary": "Ut vestibulum dignissim velit, vel aliquam massa placerat porttitor. Nunc non leo elit. Praesent non leo varius, condimentum enim ac, venenatis elit. Nulla facilisi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Morbi efficitur, justo in imperdiet dictum, leo nibh tristique lorem, nec consequat nisl sapien ut magna. Ut placerat egestas lacus, at feugiat dolor imperdiet sed. Nulla est metus, fringilla quis sodales a, placerat vel tortor. Etiam vehicula malesuada lorem convallis tempus. Curabitur porta ex at pellentesque ullamcorper. ",
                "id": 13,
                "suggestions": [
                    {
                        "id": 13,
                        "title": "TEST",
                        "authors": [
                            "J. Doe",
                        ],
                        "publication_date": "2023-11-06",
                    },
                ],
            },
        )

        with open("test.pdf", "br") as test_file:
            response = client.post("/upload_article", files={"paper": test_file}, data={"language_toggle": True})
        html = response.text
        assert "TEST" in html
        assert "J. Doe" in html
        assert "2023-11-06" in html
    
    def test_normal_get(self):
        self.r_mock.get(
            "http://ORCHESTRATOR/get_summary",
            json={
                "summary": "Ut vestibulum dignissim velit, vel aliquam massa placerat porttitor. Nunc non leo elit. Praesent non leo varius, condimentum enim ac, venenatis elit. Nulla facilisi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Morbi efficitur, justo in imperdiet dictum, leo nibh tristique lorem, nec consequat nisl sapien ut magna. Ut placerat egestas lacus, at feugiat dolor imperdiet sed. Nulla est metus, fringilla quis sodales a, placerat vel tortor. Etiam vehicula malesuada lorem convallis tempus. Curabitur porta ex at pellentesque ullamcorper. ",
                "id": 13,
                "suggestions": [
                    {
                        "id": 13,
                        "title": "TEST",
                        "authors": [
                            "J. Doe",
                        ],
                        "publication_date": "2023-11-06",
                    },
                ],
            },
        )

        with open("test.pdf", "br") as test_file:
            response = client.get("/get_summary", params={"paper_id": 1, "language_toggle": True})
        html = response.text
        assert "TEST" in html
        assert "J. Doe" in html
        assert "2023-11-06" in html
    
    def test_html_injected_get(self):
        self.r_mock.get(
            "http://ORCHESTRATOR/get_summary",
            json={
                "summary": "Ut vestibulum dignissim velit, vel aliquam massa placerat porttitor. Nunc non leo elit. Praesent non leo varius, condimentum enim ac, venenatis elit. Nulla facilisi. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Morbi efficitur, justo in imperdiet dictum, leo nibh tristique lorem, nec consequat nisl sapien ut magna. Ut placerat egestas lacus, at feugiat dolor imperdiet sed. Nulla est metus, fringilla quis sodales a, placerat vel tortor. Etiam vehicula malesuada lorem convallis tempus. Curabitur porta ex at pellentesque ullamcorper. ",
                "id": 13,
                "suggestions": [
                    {
                        "id": 13,
                        "title": "<p>TEST</p>",
                        "authors": [
                            "<p>J. Doe</p>",
                        ],
                        "publication_date": "2023-11-06",
                    },
                ],
            },
        )

        with open("test.pdf", "br") as test_file:
            response = client.get("/get_summary", params={"paper_id": 1, "language_toggle": True})
        html = response.text
        assert "TEST" in html
        assert "<p>TEST</p>" not in html
        assert "J. Doe" in html
        assert "<p>J. Doe</p>" not in html
        assert "2023-11-06" in html

if __name__ == '__main__':
    unittest.main()