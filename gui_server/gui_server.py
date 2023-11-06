from fastapi import Form, UploadFile, FastAPI
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# FastAPI needs to know where the CSS files are, otherwise using these files in a webpage will result in a 404 for that resource.
# In practise this means the website will not look as intended.
app.mount("/styles", StaticFiles(directory="html/styles"), name="styles")

# FastAPI uses decoraters to 'attach' functions to an adress.
# In this case it is a POST method because that supports uploading a file.
@app.post("/upload_article")
async def process_article(
    paper: UploadFile,
    language_toggle: Annotated[bool, Form()] = False,
    response_class=HTMLResponse):

    # This is a placeholder, because it should be handeled by other parts of the program.
    if language_toggle:
        language = "English"
    else:
        language = "Dutch"
    html_text = f"<p>This should be a summary of the file with name {paper.filename}, written in {language}.</p>"

    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response

@app.get("/", response_class=HTMLResponse)
async def main_page():
    with open("html/index.html") as file:
        html_text = file.read()

    response = HTMLResponse(content=html_text)
    response.headers["Content-Type"] = "text.html"
    return response
