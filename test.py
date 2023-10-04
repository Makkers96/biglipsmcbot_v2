# from duckduckgo_search import DDGS
# from bs4 import BeautifulSoup, NavigableString
# import requests
# import os
# import google.generativeai as palm
#
# def remove_apostrophes(input_string):
#     return input_string.replace("'", "")
#
#
# def search(user_question):
#     with DDGS() as ddgs:
#         for r in ddgs.text(f"site:wiki.albiononline.com {user_question}", max_results=10):
#             return r
#
#
# def get_url_from_search_results(search_result):
#     url = search_result['href']
#     return url
#
#
# def get_webpage_data(url):
#     request_result = requests.get(url)
#     soup = BeautifulSoup(request_result.text, 'html.parser')
#
#     table_tags = soup.find_all('table', {'class': 'wikitable'})
#
#     content_tags = []
#     content_tags_str = []
#     patch_tags = []
#
#     # grabbing tables in html
#     for tag in table_tags:
#         if "Patch Link" in str(tag):
#             patch_tags.append(tag)
#         else:
#             table_title_tag = tag.find_previous('h2')
#             if table_title_tag:
#                 content_tags.append(table_title_tag)
#                 content_tags_str.append(str(table_title_tag))
#             content_tags.append(tag)
#             content_tags_str.append(str(tag))
#
#     table_data = ''.join(content_tags_str)
#
#     # grab rest in raw text
#     body = soup.find('body')
#
#     # remove tables from the body
#     for tag in content_tags:
#         tag.decompose()
#
#     # get the text from the body
#     body_text = ""
#     for string in body.stripped_strings:
#         body_text += string + "\n"
#
#     return table_data, body_text
#
#
# # question = remove_apostrophes("What are the q slot abilities on an expert's mace?")
# # search_ressult = search(question)
# # print(search_ressult)
# # url = get_url_from_search_results(search_ressult)
# # print(url)
#
#
# table_html, text_block = get_webpage_data("https://wiki.albiononline.com/wiki/GvG_Season_11")
# print(table_html)
