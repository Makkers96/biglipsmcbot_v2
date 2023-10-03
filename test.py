from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
import os
import google.generativeai as palm

def remove_apostrophes(input_string):
    return input_string.replace("'", "")


def search(user_question):
    with DDGS() as ddgs:
        for r in ddgs.text(f"site:wiki.albiononline.com {user_question}", max_results=10):
            return r


def get_url_from_search_results(search_result):
    url = search_result['href']
    return url


def get_webpage_text(url):
    request_result = requests.get(url)
    soup = BeautifulSoup(request_result.text, 'html.parser')
    start_tag = soup.find('h1', {'class': 'firstHeading'})
    h2_tags = soup.find_all('h2')

    end_tag = None
    for line in h2_tags:
        if "Related_Patch_Notes" in str(line):
            end_tag = line
    print(f"This is endtag after the thing. {end_tag}")

    if start_tag and end_tag:
        content_tags = []
        for tag in start_tag.next_elements:
            if tag == end_tag:
                break
            content_tags.append(str(tag))

        html = ''.join(content_tags)
        return html
    else:
        return None
    # text = soup.get_text()

# question = remove_apostrophes("What are the q slot abilities on an expert's mace?")
# search_ressult = search(question)
# print(search_ressult)
# url = get_url_from_search_results(search_ressult)
# print(url)


# text_block = get_webpage_text("https://wiki.albiononline.com/wiki/GvG_Season_11")
# print(text_block)

