from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

questions = []

@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get('question')
    answer = "Sample answer for: " + question  # Replace this line with the code to generate a real answer
    questions.insert(0, {"question": question, "answer": answer})
    rendered_template = render_template('question_answer.html', q={"question": question, "answer": answer})
    return jsonify({"template": rendered_template})

@app.route('/clear', methods=['POST'])
def clear_questions():
    global questions
    questions = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
