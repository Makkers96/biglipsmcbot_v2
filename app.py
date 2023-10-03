from flask import Flask, render_template, request, session
import os
from main import search, get_url_from_search_results, remove_apostrophes, get_webpage_text, run_llm

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

@app.route("/", methods=["GET", "POST"])
def biglipsmcbot():

    if 'user_question' not in session:
        session['user_question'] = ""
    if 'llm_response' not in session:
        session['llm_response'] = ""

    if request.method == 'POST':
        if 'user_question' in request.form:
            session['user_question'] = request.form.get('user_question')

            fixed_question = remove_apostrophes(session['user_question'])
            print(f"TESTING: This is the fixed question: {fixed_question}")

            search_result = search(fixed_question)

            url_from_search = get_url_from_search_results(search_result)
            print(f"TESTING: This is the url for the question: {url_from_search}")

            webpage_text = get_webpage_text(url_from_search)

            session['llm_response'] = run_llm(session['user_question'], webpage_text)

    return render_template("biglipsmcbot.html",
                           user_question=session['user_question'],
                           llm_response=session['llm_response'],
                           )


if __name__ == "__main__":
    app.run()
