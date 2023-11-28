from fastapi import Form, UploadFile, FastAPI
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from jinja2 import Environment, PackageLoader

HTML_TEMPLATE_NAME = "results.html"

jinja_env = Environment(loader=PackageLoader("gui_server", "html"))
template = jinja_env.get_template(HTML_TEMPLATE_NAME)

app = FastAPI()

# FastAPI needs to know where the CSS files are, otherwise using these files in a webpage will result in a 404 for that resource.
# In practise this means the website will not look as intended.
app.mount("/styles", StaticFiles(directory="html/styles"), name="styles")
app.mount("/images", StaticFiles(directory="html/images"), name="styles")

# FastAPI uses decoraters to 'attach' functions to an adress.
# In this case it is a POST method because that supports uploading a file.
@app.post("/upload_article")
async def process_article(
    paper: UploadFile,
    language_toggle: Annotated[bool, Form()] = False,
    response_class=HTMLResponse
):
    # This is a placeholder, because it should be handeled by other parts of the program.
    if language_toggle:
        language = "English"
    else:
        language = "Dutch"

    request_url = "http://ORCHESTRATOR/upload_article"
    request_files = {'paper': paper.file}
    request_values = {'language_toggle': language_toggle}
    summary_data = requests.post(request_url, files=request_files, data=request_values).json()
    for suggestion in summary_data["suggestions"]:
        suggestion["href"] = f"/get_summary?paper_id={suggestion['id']}"
    html_text = template.render(summary_data)
    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response

@app.get("/get_summary")
async def get_summary(
    paper_id: int,
    language_toggle: bool = False,
    response_class=HTMLResponse
):
    # This is a placeholder, because it should be handeled by other parts of the program.
    if language_toggle:
        language = "English"
    else:
        language = "Dutch"

    request_url = "http://ORCHESTRATOR/get_summary"
    request_values = {'paper_id': paper_id, 'language_toggle': language_toggle}
    summary_data = requests.get(request_url, data=request_values).json()
    html_text = template.render(summary_data)
    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response

@app.post("/vote")
async def vote(
    paper_id: Annotated[int, Form()],
    vote: Annotated[str, Form()],
):
    request_url = "http://ORCHESTRATOR/vote"
    vote_data = {"paper_id": paper_id, "vote": vote}
    response = requests.post(request_url, data=vote_data)

    with open("html/feedback.html") as file:
        html_text = file.read()

    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response

# This is the main page (index.html) that people see first.
@app.get("/", response_class=HTMLResponse)
async def main_page():
    with open("html/index.html") as file:
        html_text = file.read()

    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response
