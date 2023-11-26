# Summarticle, your PDF-article summarizer!

## A program that asks for user inputted articles and outputs summaries of the articles in Dutch or English depending on the preference of the user.<br>

<br><img src="https://cdn-icons-png.flaticon.com/512/1949/1949624.png" width="100" height="100" /><br>

<p></p>This project is part of the Software Engineering course at Tilburg University, and represents a program that asks PDF-based articles as user input and
creates a short summary of those articles. The user can show a preference which language the summary is written in, the choices of this preference are
Dutch and English, if the summary is not sufficient to the user, the user may asks for a newly generated summary. On top of that, the user gets shown 
particular key-words on which recommendated articles are based.</p><br>

<h3>Usage instructions for end-users</h3>
<ol>
  <li>Add file in .pdf format to the pdf_database folder</li>
  <li>Implement file name as argument to the sumArticle function</li>
  <li>Summary can be obtained after approximately 3/4 minutes depending on the size of the article</li>
  <li>Implement file name as argument to the pdfKE function</li>
  <li>Keywords can be obtained and used as indicator for the article at other articles</li>
  <li>Implement summary variable name to the translArticle function if summary language desired to be Dutch</li>
  <li>Dutch summary can be obtained after approximately 10 seconds</li>
</ol><br>

<h3>Usage instructions for contributers</h3>
<ol>
  <li>After performing usage instructions, when bugs have been found, please inform the dev team</li>
</ol><br>

<h3>Contributer expectations</h3>
<p>Contributers are expected to report bugs and issues if encounterd using the code</p><br>

<h3>Known issues</h3>
<p>sumArticle function may crash once token count of implemented article surpasses 2 times the model token limit</p>


