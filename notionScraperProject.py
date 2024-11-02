import os
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from helperFunctions import split_array_by_length_with_llm

# Setting api token to connect to openai llm
load_dotenv()
api_token = os.getenv("API_TOKEN")
openai.api_key={api_token}

# Making a request to the Notion page and using BeautifulSoup to parse the html from Notion's dom
notion_url = 'https://www.notion.so/help'
response = requests.get(notion_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all pages on the left sidebar on the Notion help page
pages = soup.find_all('a', class_='toggleList_link__safdF')
links = []
for page in pages:
    articles = page.get('href').split('/help')[1]

    # Filtering out notion academy pages and category pages
    if all(x not in articles for x in ["category", "guides", "notion-academy"]):
        links.append(articles)

# Append the notion url with the appropriate article link
urls = []
for link in links:
    urls.append(notion_url + link)

# Main function processing scraped data per article into chunks
output = []
def process_data_into_chunks(arr):
    for url in urls:
        temp_chunk = []
        article_response = requests.get(url)
        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        # Find the titles per article, strip down to just the base text, and append to our temporary chunk array
        title = article_soup.find('h1', class_='title_title__DWL5N')
        title_text = title.get_text(strip=True)
        temp_chunk.append(title_text)

        # Process the main article content by finding current div tag (all necessary info falls within the specified class below)
        current_div = title.find_next('div', class_='contentfulRichText_bodyLimit__F5GOU')

        # Process every div we loop through per specific article 
        while current_div:
            
            # Dynamically checking for subtitles and headers, rather than hardcoding h2, h3, h4, etc.
            header = current_div.find(['h2', 'h3', 'h4', 'h5', 'h6'])

            # If header exists, strip down to base text and append to our temp chunk array
            if header:
                header_text = header.get_text(strip=True)
                temp_chunk.append(header_text)

            # Since we don't want to break up lists, process lists as one element (combine all consective ul or li tags into one array) and append into our temp chunk array
            list_tag = current_div.find('ul')
            if list_tag:
                list_items = [li.get_text(strip=True) for li in list_tag.find_all('li')]
                temp_chunk.append(list_items)

            # Process paragraph tags
            paragraphs = current_div.find_all('p', class_='contentfulRichText_paragraph___hjRE')
            for paragraph in paragraphs:

                # Making sure we don't add an already added list element to the temp chunk array (was running into an error that kept duplicating the previously added list array)
                if paragraph and not paragraph.find('li', class_='contentfulRichText_listItem___Swmu'):

                    # Get the text content if there are no <ul> or <li> tags inside
                    paragraph_text = paragraph.get_text(strip=True)

                    # If paragraph text is not in the last element of the array, we know we aren't adding a list element and can proceed with appending into our temp chunk array
                    if paragraph_text and paragraph_text not in temp_chunk[-1]:
                        temp_chunk.append(paragraph_text)

            # Update our current div to the next div we find with the specified class below that Notion uses
            current_div = current_div.find_next_sibling('div', class_='contentfulRichText_bodyLimit__F5GOU')

        # Process FAQ section if it exists (splitting up since FAQs uses a different class)
        faq_title = article_soup.find('h2', class_='title_title__DWL5N', string="FAQs")

        # Since not all pages have a FAQs section, checking to see if it exists on the page or not
        if faq_title:

            # Add the FAQ text to our temp chunk
            faq_header = faq_title.get_text(strip=True)
            temp_chunk.append(faq_header)

            # Find all question and answer tags
            faqs = article_soup.find_all('details', class_='faqDrawers_faq__0F7_v')
            for faq in faqs:

                # Extract questions from FAQs and append to temp chunk array
                question_text = faq.find('summary', class_='faqDrawers_question__9BX_Y').get_text(strip=True)
                temp_chunk.append(question_text)

                # Extract answers from FAQs and append to temp chunk array
                answers = faq.find('div', class_='faqDrawers_answer__G1hbB')
                if answers:
                    for answer_paragraph in answers.find_all('p'):
                        answer_text = answer_paragraph.get_text(strip=True)
                        temp_chunk.append(answer_text)

        # Splitting arrays into chunks of 750 (tried Bloom, Cohere, Huggingface, but was taking too long to run locally so went with OpenAI)
        split_array_by_length_with_llm(output, temp_chunk, 750)
    
    # Return our output array of chunks once we've gone through all article urls
    return arr

# Run main function to output chunks
chunks = process_data_into_chunks(output)
print(chunks)
print(len(chunks))