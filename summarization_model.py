from pypdf import PdfReader
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM



import torch

def pdfTE(pdfFile): # Function for text extraction from PDF.
    with open(pdfFile, "rb") as file: # Read in binary to handle breakline statements better (\n)
        pdfReader = PdfReader(file)
        for page in pdfReader.pages:
            yield page.extract_text() # Use of generator as keeping the whole article in the memory results in memory error.
            
def articleC(pdfFile): # Function to return the article in one string
    textCombiner = pdfTE(pdfFile) 
    textCombined = ""
    for text in textCombiner: # Loop over generator object to sum text of pages into one string
        textCombined += text
    return textCombined

def sumArticle1(pdfFile): # Function to summarize article per page
    if pdfFile.endswith(".pdf"):
        try:
            summarizer = AutoModelForSeq2SeqLM.from_pretrained("pszemraj/led-large-book-summary") # Model used from the huggingface hub (https://huggingface.co/pszemraj/led-large-book-summary)
            for text in pdfTE(pdfFile): # Iterate over generator
                summarizedPage = summarizer(text,max_length=100, min_length=50, do_sample=True)
                print(summarizedPage, end="\n")
                print()
        except PdfReadError:
            return 0
        except OSError:
            return 0

def sumArticle2(pdfFile): # Function to summarize article as a whole
    if pdfFile.endswith(".pdf"):
        try:
            summarizer = AutoModelForSeq2SeqLM.from_pretrained("pszemraj/led-large-book-summary") # Model used from the huggingface hub (https://huggingface.co/pszemraj/led-large-book-summary)
            articleCombined = articleC(pdfFile) # Iterate over generator
            summarizedPage = summarizer(articleCombined,max_length=500, min_length=100, do_sample=True)
            return summarizedPage = summarizer(articleCombined, max_length=1000, min_length=200, do_sample=True)
        except PdfReadError:
            return 0
        except OSError:
            return 0
    else:
        return 0

      
#pdfText = articleC("pdf_database\pdf1.pdf")
#sumArticle2("pdf_database\pdf1.pdf")
