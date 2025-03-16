from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Load the pre-trained model for sentence alignment
model = SentenceTransformer("sentence-transformers/LaBSE")

def scrape_text(url):
    """Extracts and cleans text from a given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")

    # Clean and extract text
    text = " ".join([p.get_text() for p in paragraphs])
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Splitting into sentences
    return sentences

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrapes text from provided URLs."""
    data = request.json
    english_url = data.get("english_url")
    hindi_url = data.get("hindi_url")

    if not english_url or not hindi_url:
        return jsonify({"error": "Both URLs are required"}), 400

    english_sentences = scrape_text(english_url)
    hindi_sentences = scrape_text(hindi_url)

    return jsonify({
        "english": {"sentences": english_sentences},
        "hindi": {"sentences": hindi_sentences}
    })

@app.route('/align', methods=['POST'])
def align():
    """Aligns English sentences with Hindi sentences."""
    data = request.json
    english_sentences = data.get("english_sentences", [])
    hindi_sentences = data.get("hindi_sentences", [])

    aligned_data = []
    for i, eng_sentence in enumerate(english_sentences):
        eng_embedding = model.encode(eng_sentence, convert_to_tensor=True)
        best_match = None
        best_score = -1

        for j, hin_sentence in enumerate(hindi_sentences):
            hin_embedding = model.encode(hin_sentence, convert_to_tensor=True)
            score = util.pytorch_cos_sim(eng_embedding, hin_embedding).item()

            if score > best_score:
                best_match = hin_sentence
                best_score = score

        if best_match and best_score > 0.7:  # Threshold for alignment
            aligned_data.append({
                "id": i + 1,
                "english": eng_sentence,
                "hindi": best_match
            })

    return jsonify({"aligned_data": aligned_data})

if __name__ == '__main__':
    app.run(debug=True)
