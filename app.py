#importing libraries
from flask import Flask, request, render_template, send_file # required for making a frontend using flask
import wikipedia # to interface with wikipediaa
import requests # interfacing with internet to raise requests
from bs4 import BeautifulSoup # a static web scrapping tool 
from fpdf import FPDF # to work with pdf files
import os

# flask app initiation
app = Flask(__name__)

# wikipedia user/app initiation
wikipedia.set_user_agent('MyApp/1.0')

# function to search for a wikipedia page based on user query and return a URL
def search_wikipedia(query):
    try:
        results = wikipedia.search(query)
        if results:
            page_title = results[0]
            page = wikipedia.page(page_title)
            return page.url
        else:
            return None
    except wikipedia.exceptions.DisambiguationError as e:
        return None
    except wikipedia.exceptions.PageError:
        return None
    except Exception as e:
        return None

# function to scrap a wikipedia URL
def scrape_wikipedia_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', {'id': 'firstHeading'}).text
        content = soup.find('div', {'id': 'mw-content-text'})
        paragraphs = content.find_all('p')
        page_content = '\n'.join([para.text for para in paragraphs])
        return {'title': title, 'content': page_content}
    else:
        return None

# helper functio for PDF embedding
def filter_text(text):
    return ''.join(char for char in text if ord(char) < 128)

def split_text_into_chunks(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# save the scrapped data to a pdf
def save_to_pdf(data, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=16, style='B')
    pdf.multi_cell(0, 10, filter_text(data['title']), align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    content = filter_text(data['content'])
    for chunk in split_text_into_chunks(content, 4000):
        pdf.multi_cell(0, 10, chunk)
        pdf.add_page()
    pdf.output(filename)

# Flask app for frontened
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        url = search_wikipedia(query)
        if url:
            scraped_data = scrape_wikipedia_page(url)
            if scraped_data:
                pdf_filename = f"{scraped_data['title'].replace(' ', '_')}.pdf"
                save_to_pdf(scraped_data, pdf_filename)
                return send_file(pdf_filename, as_attachment=True)
            else:
                return "Failed to retrieve the page content."
        else:
            return "Page not found!"
    return render_template('index.html')

# main function
if __name__ == '__main__':
    app.run(debug=True)

'''
http://127.0.0.1:5000/
'''