from bs4 import BeautifulSoup
import requests


def get_webpage_data(url):
    request_result = requests.get(url)
    soup = BeautifulSoup(request_result.text, 'html.parser')

    # grabbing all of the patch notes in text
    headings = soup.find_all('span', {'class': "mw-headline"})
    headings_with_h3 = []
    for heading in headings:
        full_tag = heading.find_previous('h3')
        headings_with_h3.append(full_tag)

    patch_notes = {}

    for heading in headings_with_h3:
        heading_text = heading.get_text()
        heading_content = []
        tag = heading.find_next_sibling()

        while tag is not None and 'h3' not in str(tag):
            heading_content.append(tag)
            tag = tag.find_next_sibling()

        text_under_heading = ' '.join([item.get_text() for item in heading_content])
        patch_notes[heading_text] = text_under_heading

    # deleting combat balance changes out of patch_notes dictionary so we can redo them
    if "Combat Balance Changes" in patch_notes:
        del patch_notes['Combat Balance Changes']

    # grabbing combat balance changes.
    combat_balance_changes = {}

    # create empy heading for combat balance changes incase there is a patch without them
    balance_changes_heading = None
    # if we find one, grab it in variable
    for heading in headings_with_h3:
        if "Combat Balance Changes" in str(heading):
            balance_changes_heading = heading
            break

    # if combat balance changes exist
    if balance_changes_heading is not None:
        # check for any general notes about the patch before specific items are highlighted
        current_balance_tag = balance_changes_heading.find_next_sibling()

        general_notes_list = []

        # if there are no bolds (specific items) put them all into general notes list
        while "<p><b>" not in str(current_balance_tag).replace('\n', '') and "</b></p>" not in str(current_balance_tag).replace('\n', '') and "h4" not in str(current_balance_tag):
            general_notes_list.append(current_balance_tag)
            current_balance_tag = current_balance_tag.find_next_sibling()

        # get the text and add general notes to the dictionary under general_notes
        general_notes_text = ' '.join([tag.get_text() for tag in general_notes_list])
        combat_balance_changes['general_notes'] = general_notes_text

        # now that we have hit a bold, we know it's the first item on the balance changes

        # initialize some lists
        list_of_titles = []
        list_of_changes = []
        list_of_changes_for_current_thing = []

        # doing the first title manually outside of the while loop, because it will add the content of the balance
        # changes once it finds a title. If didn't have this, it would add an empty list for the first one in list of
        # changes.
        first_weapon_patch_text = current_balance_tag.get_text()
        list_of_titles.append(first_weapon_patch_text)
        current_balance_tag = current_balance_tag.find_next_sibling()

        # while balance tag isn't to next section and it isn't nothing (end of page)
        while 'h3' not in str(current_balance_tag) and current_balance_tag is not None:
            # if tag is bold or its an h4(its a title)
            if "<p><b>" in str(current_balance_tag).replace('\n', '') and "</b></p>" in str(current_balance_tag).replace('\n', '') or "h4" in str(current_balance_tag):
                # add the title to the title list
                title_text = current_balance_tag.get_text()
                list_of_titles.append(title_text)
                # grab all of the content of changes for the previous thing and add them to the list of changes
                # change them to text first
                list_of_changes_for_current_thing_text = ' '.join([change.get_text() for change in list_of_changes_for_current_thing])
                list_of_changes.append(list_of_changes_for_current_thing_text)
                # reset the temporary list that holds content of changes
                list_of_changes_for_current_thing = []
                # go next tag
                current_balance_tag = current_balance_tag.find_next_sibling()
            else:
                # means its not a title, so add the text to temporary list to hold on to
                # once it finds a bold, it will add the temp list to the list of changes and reset the tempt list
                list_of_changes_for_current_thing.append(current_balance_tag)
                # go next tag
                current_balance_tag = current_balance_tag.find_next_sibling()

        # the last bit added. Because found end of balance changes, cuts off the content of changes for last item
        list_of_changes_for_current_thing_text = ' '.join([change.get_text() for change in list_of_changes_for_current_thing])
        list_of_changes.append(list_of_changes_for_current_thing_text)

        # checking to make sure we got the same amount of titles as content for changes
        if len(list_of_titles) == len(list_of_changes):
            # zip them together and add them to the dict.
            for k, v in zip(list_of_titles, list_of_changes):
                combat_balance_changes[k] = v
        else:
            print(f"Error with {url} patch notes. Got different nubmer of combat balance change headings, and changes. (len:list_of_titles and len:list_of_changes was different)")

    else:
        print("No 'Combat Balance Changes' heading found.")

    # add our combat balance changes to the patch_notes
    patch_notes['Combat Balance Changes'] = combat_balance_changes

    # grabbing patch name and date
    patch_name_html = soup.find('th', {'class': 'infoboxname'})
    patch_name_string = patch_name_html.get_text().replace('\n', '')
    patch_date_html = soup.find_all('tr')
    patch_date_string = ""
    for tag in patch_date_html:
        if 'Date' in str(tag):
            tag_with_text_date = tag.find_next()
            tag_with_text_actual_date = tag_with_text_date.find_next('td')
            patch_date_string = tag_with_text_actual_date.get_text().replace('\n', '')

    content = {}
    content['patch_name'] = patch_name_string
    content['patch_date'] = patch_date_string
    content['patch_notes'] = patch_notes

    return content


def get_patch_note_links():
    request_result = requests.get("https://wiki.albiononline.com/wiki/Patch_notes")
    soup = BeautifulSoup(request_result.text, 'html.parser')
    a_tags = soup.find_all('a')
    short_links = []
    for tag in a_tags:
        if "href" in tag.attrs:
            short_links.append(tag['href'])

    patch_short_links = []
    for link in short_links:
        if "wiki/Version_" in link:
            patch_short_links.append(link)

    patch_links = []
    for short_link in patch_short_links:
        short_link = f"https://wiki.albiononline.com{short_link}"
        patch_links.append(short_link)

    return patch_links


arcane_patch_notes = []
axe_patch_notes = []
bow_patch_notes = []
crossbow_patch_notes = []
curse_patch_notes = []
dagger_patch_notes = []
fire_patch_notes = []
frost_patch_notes = []
hammer_patch_notes = []
holy_patch_notes = []
mace_patch_notes = []
nature_patch_notes = []
quarterstaff_patch_notes = []
spear_patch_notes = []
sword_patch_notes = []
war_glove_patch_notes = []
off_hand_patch_notes = []
helmets_patch_notes = []
armors_patch_notes = []
shoes_patch_notes = []


def pull_combat_balance_notes(patch_content):
    # check if there are combat balance changes
    if 'patch_notes' in patch_content:
        if 'Combat Balance Changes' in patch_content['patch_notes']:
            combat_changes = patch_content['patch_notes']['Combat Balance Changes']
            for key in combat_changes:
                if "Arcane" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    arcane_patch_notes.append(changes)
                if "Axe" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    axe_patch_notes.append(changes)
                if "Bow" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    bow_patch_notes.append(changes)
                if "Crossbow" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    crossbow_patch_notes.append(changes)
                if "Curse" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    curse_patch_notes.append(changes)
                if "Dagger" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    dagger_patch_notes.append(changes)
                if "Fire" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    fire_patch_notes.append(changes)
                if "Frost" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    frost_patch_notes.append(changes)
                if "Hammer" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    hammer_patch_notes.append(changes)
                if "Holy" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    holy_patch_notes.append(changes)
                if "Mace" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    mace_patch_notes.append(changes)
                if "Nature" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    nature_patch_notes.append(changes)
                if "Quarter" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    quarterstaff_patch_notes.append(changes)
                if "Spear" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    spear_patch_notes.append(changes)
                if "Sword" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    sword_patch_notes.append(changes)
                if "glove" in key.lower():
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    war_glove_patch_notes.append(changes)
                if "shield" or "sarcophagus" or "caitiff" or "facebreaker" or "astral" or "torch" or "mistcaller" or "leering" or "crypt" or "sacred" or "tome" or "eye" or "muisak" or "taproot" or "celestial" in key.lower():
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    off_hand_patch_notes.append(changes)
                if "Helmet" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    helmets_patch_notes.append(changes)
                if "Armor" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    armors_patch_notes.append(changes)
                if "Shoe" in key:
                    changes = {}
                    changes['patch_date'] = patch_content['patch_date']
                    changes['patch_name'] = patch_content['patch_name']
                    changes['patch_notes'] = combat_changes[key]
                    shoes_patch_notes.append(changes)

        else:
            print(f"Error. No combat balance changes found.")
    else:
        print(f"Error. No combat balance changes found.")

patch_links = get_patch_note_links()
short_patch_links = patch_links[:30]
# # test
# print(short_patch_links)

# test_patch_links = ['https://wiki.albiononline.com/wiki/Version_22.120.1', 'https://wiki.albiononline.com/wiki/Version_22.110.1', 'https://wiki.albiononline.com/wiki/Version_22.100.1', 'https://wiki.albiononline.com/wiki/Version_22.090.1', 'https://wiki.albiononline.com/wiki/Version_22.080.1', 'https://wiki.albiononline.com/wiki/Version_22.070.1', 'https://wiki.albiononline.com/wiki/Version_22.060.1', 'https://wiki.albiononline.com/wiki/Version_22.050.1', 'https://wiki.albiononline.com/wiki/Version_22.040.1', 'https://wiki.albiononline.com/wiki/Version_21.030.1', 'https://wiki.albiononline.com/wiki/Version_21.020.1', 'https://wiki.albiononline.com/wiki/Version_21.010.1', 'https://wiki.albiononline.com/wiki/Version_21.000.1', 'https://wiki.albiononline.com/wiki/Version_20.070.1', 'https://wiki.albiononline.com/wiki/Version_20.060.1', 'https://wiki.albiononline.com/wiki/Version_20.050.1', 'https://wiki.albiononline.com/wiki/Version_20.040.1', 'https://wiki.albiononline.com/wiki/Version_20.030.1', 'https://wiki.albiononline.com/wiki/Version_20.020.1', 'https://wiki.albiononline.com/wiki/Version_20.010.1', 'https://wiki.albiononline.com/wiki/Version_20.000.1', 'https://wiki.albiononline.com/wiki/Version_19.080.1', 'https://wiki.albiononline.com/wiki/Version_19.070.1', 'https://wiki.albiononline.com/wiki/Version_19.060.1', 'https://wiki.albiononline.com/wiki/Version_19.050.1', 'https://wiki.albiononline.com/wiki/Version_19.040.1', 'https://wiki.albiononline.com/wiki/Version_19.030.1', 'https://wiki.albiononline.com/wiki/Version_19.020.1', 'https://wiki.albiononline.com/wiki/Version_19.010.1', 'https://wiki.albiononline.com/wiki/Version_19.000.1']

patches_data = []
test_counter = 0
for link in short_patch_links:
    collected_data = get_webpage_data(link)
    # add data to a list of all the patches
    patches_data.append(collected_data)
    # fill our weapon/armor patch notes data
    pull_combat_balance_notes(collected_data)
    # test
    test_counter += 1
    print(f"Finished with {link}. Total complete: {test_counter}")
