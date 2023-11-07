import responses
from responses import matchers
import uvicorn

# This code will add mock responses to fake the server connection with the orchestrator.
# After adding these responses the server gets started;
# any responses not listed here will give an error.
with responses.RequestsMock() as rsps:
    rsps.add(
        responses.POST,
        "http://ORCHESTRATOR/upload_article",
        json={
            "summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla venenatis commodo augue, feugiat vestibulum turpis molestie quis. Cras eu lacus velit. Praesent metus erat, scelerisque ut volutpat ac, mollis ac enim. Morbi hendrerit orci in varius porta. Donec viverra metus sed ante consectetur, ac sagittis urna eleifend. Vivamus maximus dignissim semper. Phasellus non porttitor velit, eu dictum est. Proin molestie facilisis fringilla. Maecenas cursus, massa a hendrerit dignissim, dolor ipsum pretium sapien, et euismod mauris eros eget tortor. Sed sed molestie justo, id sollicitudin diam. Phasellus gravida dignissim quam, ac vestibulum ipsum venenatis nec. Fusce consectetur in metus quis consequat. Morbi tempor rutrum mauris ut euismod.",
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

    uvicorn.run("gui_server:app")