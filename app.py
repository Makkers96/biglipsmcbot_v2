from flask import Flask, render_template, request, session
import os
from main import search, get_url_from_search_results, remove_apostrophes, get_webpage_text, run_llm_general, get_q_subjects, \
    read_html_tables, get_webpage_data, run_llm_patch_notes

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

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')

            subjects_question = get_q_subjects(session['user_question'])

            fixed_question = remove_apostrophes(subjects_question)

            search_result = search(fixed_question)

            url_from_search = get_url_from_search_results(search_result)
            print(f"TESTING: This is the url for the question: {url_from_search}")

            webpage_html_tables, webpage_text, patch_details = get_webpage_data(url_from_search)

            session['llm_response'] = run_llm_general(session['user_question'], webpage_html_tables, webpage_text)

    return render_template("general.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           )


@app.route("/patch_notes", methods=["GET", "POST"])
def patch_notes():
    if 'user_question' not in session:
        session['user_question'] = ""
    if 'llm_response' not in session:
        session['llm_response'] = ""

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')

            subjects_question = get_q_subjects(session['user_question'])

            fixed_question = remove_apostrophes(subjects_question)

            search_result = search(fixed_question)

            url_from_search = get_url_from_search_results(search_result)
            print(f"TESTING: This is the url for the question: {url_from_search}")

            webpage_html_tables, webpage_text, patch_details = get_webpage_data(url_from_search)

            session['llm_response'] = run_llm_patch_notes(session['user_question'], patch_details)

    return render_template("patch_notes.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           )


if __name__ == "__main__":
    app.run()
