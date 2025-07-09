#use beautifulsoup to extract tags, text, attributes
#HTML parsing engine

from bs4 import BeautifulSoup

file_path = "data/raw_html/pst_1.html"

# open and read the html file
with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

#parse with beautiful soup
# html.parser is the parser that Beautiful soup uses, this one is built-in. 
# a parser is an engine that reads and interprets the HTML/XML structure, converting it into a tree of objectss
soup = BeautifulSoup(html_content, "html.parser")

print(f"Contents: {soup}\n")

