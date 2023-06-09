# pip install Flask
# pip install langchain
# pip install openai
# pip install pypdf
# pip install tiktoken
# pip install faiss-cpu

from flask import Flask, render_template, request, jsonify
from classes import AnswerBot, PDFStoreProvider, RetrievalQAQueryProvider, ConversationalQueryProvider

app = Flask(__name__)

questions = []
provider = PDFStoreProvider("./AnswersList.pdf")
store = provider.store()
query = ConversationalQueryProvider(store)
bot = AnswerBot(query)

@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get('question')
    answer = bot.get_answer(question)
    questions.insert(0, {"question": question, "answer": answer})
    rendered_template = render_template('question_answer.html', q={"question": question, "answer": answer})
    return jsonify({"template": rendered_template})

@app.route('/clear', methods=['POST'])
def clear_questions():
    global questions
    questions = []
    query.clear_history()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
