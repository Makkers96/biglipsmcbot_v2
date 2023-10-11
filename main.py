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


def get_webpage_data(url):
    request_result = requests.get(url)
    soup = BeautifulSoup(request_result.text, 'html.parser')

    table_tags = soup.find_all('table', {'class': 'wikitable'})

    content_tags = []
    content_tags_str = []
    patch_tags = []
    patch_tags_str = []

    # grabbing tables in html, patch notes in plain text
    for tag in table_tags:
        if "Patch Link" in str(tag):
            patch_title_tag = tag.find_previous('h2')
            if patch_title_tag:
                patch_tags.append(patch_title_tag)
                patch_tags_str.append(str(patch_title_tag))
            patch_tags.append(tag)
            patch_tags_str.append(str(tag))
        else:
            table_title_tag = tag.find_previous('h2')
            if table_title_tag:
                content_tags.append(table_title_tag)
                content_tags_str.append(str(table_title_tag))
            content_tags.append(tag)
            content_tags_str.append(str(tag))

    table_data = ''.join(content_tags_str)
    # if table data too much, chop off the end.
    if len(table_data) >= 20000:
        table_data = table_data[:20000]

    patch_data = ' '.join([tag.get_text() for tag in patch_tags])


    # grab rest in raw text
    body = soup.find('body')

    # remove tables from the body
    for tag in table_tags:
        tag.decompose()

    # get the text from the body
    body_text = ""
    for string in body.stripped_strings:
        body_text += string + "\n"

    return table_data, body_text, patch_data


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
        temperature=0,
        max_output_tokens=128,
    )

    result = completion.result
    return result


def read_html_tables(html_tables):
    prompt = f"""Take the following html table(s), and for each one, transcribe it into simple readable text.

        HTML Table(s): {html_tables}
        
        Tables as Simple Text:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=1024,
    )

    result = completion.result
    return result


def run_llm_general(user_question, reference_tables, reference_text):
    prompt = f"""You are a helpful virtual assistant named Big Lips McBot that answers questions about the video game albion online.
    If you do not know the answer to the question, provide any helpful information that you can about the question.
    If the answer cannot be found in the information provided, respond that you cannot find the answer, and ask the user to ask their question in a different way.
    Respond in full sentences.
    Use the following information to answer the following question.

    User Question: {user_question}

    Information: 
    {reference_text}
    {reference_tables}

    Big Lips McBot Answer:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=512,
    )

    result = completion.result
    return result


def run_llm_patch(user_question, patch_data):
    prompt = f"""You are a helpful virtual assistant named Big Lips McBot that answers questions about the video game albion online.
    If you do not know the answer to the question, provide any helpful information that you can about the question.
    If the answer cannot be found in the information provided, respond that you cannot find the answer, and ask the user to ask their question in a different way.
    Respond in full sentences.
    Use the following information to answer the following question.

    User Question: {user_question}

    Information: {patch_data}

    Big Lips McBot Answer:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=512,
    )

    result = completion.result
    return result

def get_patch_name_from_question(user_question):
    prompt = f"""Take the following question and respond with the exact patch name found in the question from the following list.
    If the patch name is not found in the question, respond simply with "None".
    
    List of Patch Names: ['Beyond the Veil Patch 12', 'Beyond the Veil Patch 11 and Hotfix 1, 2', 'Beyond the Veil Patch 10', 'Beyond the Veil Patch 9', 'Knightfall Midseason Patch (Beyond the Veil Patch 8 and Hotfix 1, 2)', 'Beyond the Veil Patch 7', 'Beyond the Veil Patch 6 and Hotfix 6.1', 'Beyond the Veil Patch 5', 'Beyond the Veil Patch 4', 'Beyond the Veil Patch 3', 'Beyond the Veil Patch 2', 'Beyond the Veil Patch 1', 'Beyond the Veil Update', 'Into the Fray Patch 7', 'Into the Fray Patch 6', 'Into the Fray Patch 5', 'Into the Fray Patch 4 / Arcane and Frost Patch', 'Into the Fray Patch 3', 'Into the Fray Patch 2 (+ Living Legends Event)', 'Into the Fray Patch 1', 'Into the Fray Update', 'Lands Awakened Patch 8', 'Lands Awakened Patch 7', 'Lands Awakened Patch 6', 'Lands Awakened Patch 5', 'Lands Awakened Patch 4', 'Lands Awakened Patch 3', 'Lands Awakened Patch 2', 'Lands Awakened Patch 1', 'Lands Awakened Update']
    
    User Question: What was the change to war gloves in beyond the veil 5?
    Patch Name: Beyond the Veil Patch 5
    
    User Question: What was the patch called that dropped on december 1, 2022?
    Patch Name: None
    
    User Question: What was the main changes in the lands awaken update?
    Patch Name: Lands Awakened Update
    
    User Question: What was the arcane change in the first into the fray patch?
    Patch Name: Into the Fray Patch 1
    
    User Question: What was the other name for the knightfall midseason patch?
    Patch Name: Knightfall Midseason Patch (Beyond the Veil Patch 8 and Hotfix 1, 2)
    
    User Question: What is 2+2
    Patch Name: None
    
    User Question: how many sword changes were in btv 5?
    Patch Name: Beyond the Veil Patch 5

    User Question: {user_question}
    Patch Name:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=128,
    )

    result = completion.result
    return result

def check_which_patch_name(list_of_patches, llm_patch_response):
    if llm_patch_response == "None":
        return None
    else:
        for patch in list_of_patches:
            patch_name = patch['patch_name']
            if patch_name == llm_patch_response:
                return patch
        return None



def get_patch_date_from_question(user_question):
    prompt = f"""Take the following question and respond with the exact patch date found in the question from the following list.
    If the specific patch date is not found in the question, respond simply with "None".

    List of Patch Names: ['14 August 2023', '5 July 2023', '19 June 2023', '30 May 2023', '8 May 2023', '29 March 2023', '13 March 2023', '7 March 2023', '13 February 2023', '9 January 2023', '14 December 2022', '1 December 2022', '21 November 2022', '5 October 2022', '14 September 2022', 'August 25, 2022', 'August 9, 2022', 'July 19, 2022', 'July 5, 2022', '20 June 2022', '8 June 2022', '25 April 2022', '30 March 2022', '02 March 2022', '09 February 2022', '26 January 2022', '12 January 2022', '20 December 2021', '13 December 2021', '24 November 2021']
    
    User Question: What was the patch from june 19th 2023?
    Patch Date: 19 June 2023

    User Question: What wargloves changes happened june 2022
    Patch Date: None

    User Question: In the nov 24 patch 2021, which guild won the season?
    Patch Date: 24 November 2021

    User Question: {user_question}
    Patch Date:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=128,
    )

    result = completion.result
    return result


def check_which_patch_date(list_of_patches, llm_date_response):
    if llm_date_response == "None":
        return None
    else:
        for patch in list_of_patches:
            patch_date = patch['patch_date']
            if patch_date == llm_date_response:
                return patch
        return None


def get_patch_item_from_question(user_question):
    prompt = f"""Take the following question and respond with the exact item type in found in the question from the following list.
    If the question contains an item similar to one on the list, respond with that item type.
    If the specific item / item type, or anything close to it, is not found in the question, respond simply with "None".

    List of Item Types:
    Arcane (Includes any: 1h arcane, great arcane, enigmatic, witchwork, whichwork, occult, malevolent locus, evensong)
    Axe (Includes any: 1h axe, battleaxe, greataxe, great axe, halberd, carrioncaller, infernal scythe, bear paws)
    Bow (Includes any: normal bow, warbow, longbow, whispering bow, wailing bow, bow of badon)
    Crossbow (Includes any: 1h/2h crossbow, light crossbow, heavy crossbow, weeping repeater, boltcasters, siegebow, xbow)
    Curse (Includes any: 1h cursed, great cursed, demonic , lifecurse, cursed skull, damnation, shadowcaller)
    Dagger (Includes any: 1h dagger, dagger pair, claws, bloodletter, demonfang, deathgivers)
    Fire (Includes any: 1h fire, great fire, infernal, wildfire, brimstone, blazing, dawnsong)
    Frost (Includes any: 1h frost, great frost, glacial, hoarfrost, icicle, permafrost prism, chillhowl)
    Hammer (Includes any: 1h hammer, polehammer, great hammer, tombhammer, forge hammers, grovekeeper, pog log)
    Holy (Includes any: divine, lifetouch, fallen, redemption, hallowfall)
    Mace (Includes any: morning star, bedrock, incubus, camlann)
    Nature (Includes any: wild, druidic, blight, rampant, ironroot)
    Quarterstaff (Includes any: iron-clad, double bladed, black monk, bms, soulscythe, staff of balance)
    Spear (Includes any: pike, glaive, heron, spirithunter, trinity)
    Sword (Includes any: broadsword, claymore, duals, clarent, carving, galatine pair)
    Gloves (Includes any: battle bracers, spiked gauntlets, brawler gloves, ravenstrike cestus, ursine maulers, hellfire hands, fists of avalon)
    Off-hand (Includes any: shield, sarcophagus, caitiff, facebreaker, torch, mistcaller, leering cane, cryptcandle, tome of spells, eye of secrets, muisak, taproot, celestial censer)
    Helmet (Includes any: hoods, cowls, helmets, helm, cap)
    Armor (Includes any: robe, jacket, armors, garb)
    Shoe (Includes any: shoes, sandals, boots, workboots)
    
    User Question: What was the last change for locus?
    Item Type: Arcane

    User Question: What was the change to carrion in the most recent patch?
    Item Type: Axe
    
    User Question: What's the cooldown of badons E?
    Item Type: Bow
    
    User Question: How many times was scythe buffed in the last 5 patches?
    Item Type: Axe
    
    User Question: What was the first change to merc jacket?
    Item Type: Armor
    
    User Question: How many changes to sacrophagus have their been in the last 5 patches?
    Item Type: Off-hand
    
    User Question: How are you doing today?
    Item Type: None

    User Question: {user_question}
    Item Type:"""

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=128,
    )

    result = completion.result
    return result


def check_llm_patch_item_response(llm_patch_item_response):
    if llm_patch_item_response == "None":
        return None
    else:
        return llm_patch_item_response
