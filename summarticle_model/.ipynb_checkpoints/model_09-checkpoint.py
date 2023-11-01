from pypdf import PdfReader
from transformers import pipeline
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
    summarizer = pipeline("summarization", model="pszemraj/led-large-book-summary") # Model used from the huggingface hub (https://huggingface.co/pszemraj/led-large-book-summary)
    for text in pdfTE(pdfFile): # Iterate over generator
        summarizedPage = summarizer(text,max_length=100, min_length=50, do_sample=True)
        print(summarizedPage, end="\n")
        print()

def sumArticle2(pdfFile): # Function to summarize article as a whole
    summarizer = pipeline("summarization", model="pszemraj/led-large-book-summary") # Model used from the huggingface hub (https://huggingface.co/pszemraj/led-large-book-summary)
    articleCombined = articleC(pdfFile) # Iterate over generator
    summarizedPage = summarizer(articleCombined,max_length=500, min_length=100, do_sample=True)
    print(summarizedPage, end="\n")

      
pdfText = articleC("pdf_database\pdf1.pdf")

sumArticle2("pdf_database\pdf1.pdf")


# =============================================================================
# These tests were done with function: sumArticle1
#
# Test 1 results (max length=300, min length=100):
#     - Program took 20 minutes to produce the article page for page
#     - Summaries were accurate with important and clear information
#     - Spelling errors? yes
# 
# Test 2 results (max length=10, min length = 3):
#     - Program took 2 minutes to produce the article page for page
#     - Summaries were totally not accurate, more like broken sentences
#     - Spelling errors? yes
# 
# Test 3 results (max length=50, min length = 30):
#     - Program took 4 minutes to produce the article page for page
#     - Summaries seemed somewhat accurate, sentences started the same as with test 2? weird.. is model not random?
#     - Spelling errors? yes
# 
# Test 4 results (max length=100, min length=50):
#     - Program took 5 minutes to produce the article page for page
#     - Summaries seemed accurate despite sentences being cut off
#     - Spelling errors? little
#
# These tests were done with function sumArticle2
#
# Test 1 results (max length=300, min length=100):
#     - Program took 2 minutes to produce the article
#     - Summary explains content of the pdf briefly, mentioning some techniques
#       used in the article, but not much in depth information.
#     - Seemed written as a whole, no sentences cut off.
#
# Test 2 results (max length=300, min length=100):
#     - Program took 2,5 minutes to produce the article
#     - Summary explains content of the pdf well, goes indepth quite a bit.
#     - Some sentences were cut off.
#     - Running the model with same parameters resulted in 2 different summaries.
# =============================================================================

# [{'summary_text': 'This paper discusses several different algorithmic models to predict software development time and other management parameters. The most commonly used is the Putnam model, but it is not reliable in all cases. In this paper, the authors propose a new model that predicts much more accurately than the putnam model. The authors examine several different statistical methods to predict real-time performance of this model. They also discuss several different types of prediction such as the "routine" or "learning curve," which are used to predict future performance of a particular task. They conclude that this model can be useful for predicting future performance on a broad range of industrial applications as well as specific ones.'}]