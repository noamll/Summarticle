import responses
from responses import matchers
import uvicorn

# This code will add mock responses to fake the server connection with the orchestrator.
# After adding these responses the server gets started;
# any responses not listed here will give an error.
with responses.RequestsMock() as rsps:
    # Expected results for getting a summary from file upload.
    rsps.add(
        responses.POST,
        "http://ORCHESTRATOR/upload_article",
        json={
            "paper_id": 13,
        },
    )

    # Expected results for getting a summery by id, for example for getting the related articles.
    rsps.add(
        responses.GET,
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

    rsps.add(
        responses.POST,
        "http://ORCHESTRATOR/vote",
        json={
            "result": True
        }
    )

    uvicorn.run("gui_server:app")