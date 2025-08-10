from flask import Flask, render_template, request, jsonify
from main import run_agent

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def research():
    data = request.get_json()
    topic = data.get('topic')
    questions = data.get('questions')
    if not topic or not questions:
        return jsonify({'error': 'Topic and questions are required'}), 400

    response = run_agent(topic, questions)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
