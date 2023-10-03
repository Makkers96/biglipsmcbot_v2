# pip install duckduckgo-search google-generativeai requests beautifulsoup4 flask

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
import os
import google.generativeai as palm

# llm initialization
key = os.getenv('google_key')

palm.configure(api_key=key)

models = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
]

model = models[0].name


def search(user_question):
    with DDGS() as ddgs:
        for r in ddgs.text(f"site:wiki.albiononline.com {user_question}", max_results=1):
            return r


def get_url_from_search_results(search_result):
    url = search_result['href']
    return url


# make a func to remove apostrophies from a string
def remove_apostrophes(input_string):
    return input_string.replace("'", "")


def get_webpage_text(url):
    request_result = requests.get(url)
    soup = BeautifulSoup(request_result.text, 'html.parser')
    text = soup.get_text()
    return text



def get_q_subjects(question):
    prompt = f"""Take the following question and respond with the essential elements or key subject(s). Respond only with these key subject(s).
        
        Question: What are the Q slot ability options for an expert's mace?
        Key Subject(s): Q slot ability, expert's mace
        
        Question: Is it worth it to buy a personal island?
        Key Subject(s): personal island
        
        Question: How is average estimated market value calculated?
        Key Subject(s): average estimated market value

        Question: {question}
        Key Subject(s):"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=128,
    )

    result = completion.result
    return result

def run_llm(user_question, reference_text):
    prompt = f"""You are a helpful virtual assistant named Big Lips McBot that answers questions about the video game albion online.
    If you do not know the answer to the question, provide any helpful information that you can about the question, or simply say that you could not find the answer.
    Respond in full sentences.
    Use the following information to answer the following question.

    Question: {user_question}

    Information: {reference_text}

    Answer:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0.2,
        max_output_tokens=128,
    )

    result = completion.result
    return result

