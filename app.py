from flask import Flask, render_template, request, jsonify
from scraper import scrape_website
from aligner import align_sentences

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    english_url = data.get('english_url')
    hindi_url = data.get('hindi_url')

    if not english_url or not hindi_url:
        return jsonify({'error': 'Both URLs are required'}), 400

    english_data = scrape_website(english_url, language='en')
    hindi_data = scrape_website(hindi_url, language='hi')

    return jsonify({'english': english_data, 'hindi': hindi_data})

@app.route('/align', methods=['POST'])
def align():
    data = request.json
    english_sentences = data.get('english_sentences', [])
    hindi_sentences = data.get('hindi_sentences', [])

    aligned_data = align_sentences(english_sentences, hindi_sentences)

    return jsonify({'aligned_data': aligned_data})

if __name__ == '__main__':
    app.run(debug=True)
