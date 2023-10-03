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

# question = remove_apostrophes("What are the q slot abilities on an expert's mace?")
# search_ressult = search(question)
# print(search_ressult)
# url = get_url_from_search_results(search_ressult)
# print(url)