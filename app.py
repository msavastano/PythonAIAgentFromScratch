from flask import Flask, render_template, request, jsonify
from main import run_agent

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/research', methods=['POST'])
def research():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query not provided'}), 400

    response = run_agent(query)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
