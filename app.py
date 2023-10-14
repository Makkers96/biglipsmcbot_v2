from flask import Flask, render_template, request, session
import markdown
import os
from main import search, get_url_from_search_results, remove_apostrophes, get_webpage_text, run_llm_general, \
    get_q_subjects, \
    read_html_tables, get_webpage_data, run_llm_patch_item, check_which_patch_name, get_patch_name_from_question, \
    get_patch_date_from_question, check_which_patch_date, get_patch_item_from_question, check_llm_patch_item_response, \
    format_list_for_context, format_dict_for_context, run_llm_specific_patch
from data import patches_data, arcane_patch_notes, axe_patch_notes, bow_patch_notes, crossbow_patch_notes, \
    curse_patch_notes, dagger_patch_notes, fire_patch_notes, frost_patch_notes, hammer_patch_notes, holy_patch_notes, \
    mace_patch_notes, nature_patch_notes, quarterstaff_patch_notes, spear_patch_notes, sword_patch_notes, \
    war_glove_patch_notes, off_hand_patch_notes, helmets_patch_notes, armors_patch_notes, shoes_patch_notes

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')


@app.route("/", methods=["GET", "POST"])
def homepage():
    return render_template('homepage.html')


@app.route("/general", methods=["GET", "POST"])
def general():
    if 'user_question' not in session:
        session['user_question'] = ""
    if 'llm_response' not in session:
        session['llm_response'] = ""
    if 'source_link' not in session:
        session['source_link'] = ""

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')
            print(f"TESTING: This is the user's' question. {session['user_question']}")

            subjects_question = get_q_subjects(session['user_question'])

            fixed_question = remove_apostrophes(subjects_question)

            search_result = search(fixed_question)

            if search_result is None:
                error_message = "ERROR: Search resulted in nothing. Please ask about Albion Online."
                return render_template("general.html",
                                       error_message=error_message,
                                       user_question=session['user_question'],
                                       llm_response=session['llm_response'],
                                       source_link=session['source_link'],
                                       )

            url_from_search = get_url_from_search_results(search_result)
            session['source_link'] = url_from_search
            print(f"TESTING: This is the url for the question: {url_from_search}")

            webpage_html_tables, webpage_text, patch_details = get_webpage_data(url_from_search)

            session['llm_response'] = run_llm_general(session['user_question'], webpage_html_tables, webpage_text)

    return render_template("general.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           source_link=session['source_link'],
                           )


@app.route("/specific_patch", methods=["GET", "POST"])
def specific_patch():
    if 'user_question' not in session:
        session['user_question'] = ""
    if 'llm_response' not in session:
        session['llm_response'] = ""

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')
            print(f"TESTING: This is the user's' question. {session['user_question']}")

            llm_patch_name_response = get_patch_name_from_question(session['user_question'])
            print(f"TEST TEST: llm_response getting patch name: {llm_patch_name_response}")
            patch_for_context = check_which_patch_name(patches_data, llm_patch_name_response)

            if patch_for_context is None:
                # go check for patch date
                llm_patch_date_response = get_patch_date_from_question(session['user_question'])
                patch_for_context = check_which_patch_date(patches_data, llm_patch_date_response)
                if patch_for_context is None:
                    error_message = "Could not find patch you were asking for. Please double check your question, and report in discord. (Patch might not be in database yet.)"
                    return render_template("specific_patch.html",
                                           error_message=error_message,
                                           user_question=session['user_question'],
                                           llm_response=session['llm_response'],
                                           )
                else:
                    test_formatted_patch_info = format_dict_for_context(patch_for_context)
                    print(f"TEST: Formatted specific patch context: {test_formatted_patch_info}")
                    session['llm_response'] = run_llm_specific_patch(session['user_question'], patch_for_context)
            else:
                test_formatted_patch_info = format_dict_for_context(patch_for_context)
                print(f"TEST: Formatted specific patch context: {test_formatted_patch_info}")
                session['llm_response'] = run_llm_specific_patch(session['user_question'], patch_for_context)

            print(f"TEST TEST: This is the llm response in specific_patch: {session['llm_response']}")

    if session['llm_response'] is None:
        error_message = "There was an issue with bot response (response = None), please report in discord."
        return render_template("specific_patch.html",
                               error_message=error_message,
                               user_question=session['user_question'],
                               llm_response=session['llm_response'],
                               )
    else:
        session['llm_response'] = markdown.markdown(session['llm_response'])

    return render_template("specific_patch.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           )


@app.route("/patch_items", methods=["GET", "POST"])
def patch_items():
    if 'user_question' not in session:
        session['user_question'] = ""
    if 'llm_response' not in session:
        session['llm_response'] = ""

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')
            print(f"TESTING: This is the user's' question. {session['user_question']}")

            llm_patch_item_response = get_patch_item_from_question(session['user_question'])

            check_response = check_llm_patch_item_response(llm_patch_item_response)
            print(f"TEST TEST: In patch_items. Question asked, check_response: {check_response}")

            if check_response is None:
                error_message = "Could not find the item you were asking about. Please double check your question, and report in discord."
                return render_template("patch_items.html",
                                       error_message=error_message,
                                       user_question=session['user_question'],
                                       llm_response=session['llm_response'],
                                       )
            else:
                if llm_patch_item_response == "Arcane":
                    patch_item_context = arcane_patch_notes
                elif llm_patch_item_response == "Axe":
                    patch_item_context = axe_patch_notes
                elif llm_patch_item_response == "Bow":
                    patch_item_context = bow_patch_notes
                elif llm_patch_item_response == "Crossbow":
                    patch_item_context = crossbow_patch_notes
                elif llm_patch_item_response == "Curse":
                    patch_item_context = curse_patch_notes
                elif llm_patch_item_response == "Dagger":
                    patch_item_context = dagger_patch_notes
                elif llm_patch_item_response == "Fire":
                    patch_item_context = fire_patch_notes
                elif llm_patch_item_response == "Frost":
                    patch_item_context = frost_patch_notes
                elif llm_patch_item_response == "Hammer":
                    patch_item_context = hammer_patch_notes
                elif llm_patch_item_response == "Holy":
                    patch_item_context = holy_patch_notes
                elif llm_patch_item_response == "Mace":
                    patch_item_context = mace_patch_notes
                elif llm_patch_item_response == "Nature":
                    patch_item_context = nature_patch_notes
                elif llm_patch_item_response == "Quarterstaff":
                    patch_item_context = quarterstaff_patch_notes
                elif llm_patch_item_response == "Spear":
                    patch_item_context = spear_patch_notes
                elif llm_patch_item_response == "Sword":
                    patch_item_context = sword_patch_notes
                elif llm_patch_item_response == "Gloves":
                    patch_item_context = war_glove_patch_notes
                elif llm_patch_item_response == "Off-hand":
                    patch_item_context = off_hand_patch_notes
                elif llm_patch_item_response == "Helmet":
                    patch_item_context = helmets_patch_notes
                elif llm_patch_item_response == "Armor":
                    patch_item_context = armors_patch_notes
                elif llm_patch_item_response == "Shoe":
                    patch_item_context = shoes_patch_notes
                else:
                    error_message = f"Could not find the item you were asking about (Item: {llm_patch_item_response}. Please double check your question, and report in discord."
                    return render_template("patch_items.html",
                                           error_message=error_message,
                                           user_question=session['user_question'],
                                           llm_response=session['llm_response'],
                                           )

                formatted_context = format_list_for_context(patch_item_context)
                print(f"This is the patch_item_context going in: {formatted_context}")
                session['llm_response'] = run_llm_patch_item(session['user_question'], formatted_context)
                print(f"TEST TEST: This is the llm response in patch_item: {session['llm_response']}")

    if session['llm_response'] is None:
        error_message = "There was an issue with bot response (response = None), please report in discord."
        return render_template("patch_items.html",
                               error_message=error_message,
                               user_question=session['user_question'],
                               llm_response=session['llm_response'],
                               )
    else:
        session['llm_response'] = markdown.markdown(session['llm_response'])

    return render_template("patch_items.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           )


if __name__ == "__main__":
    app.run()
