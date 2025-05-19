from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

model = SentenceTransformer('sentence-transformers/LaBSE')

def clean_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def split_english_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [clean_text(s) for s in sentences if s.strip()]

def split_hindi_sentences(text):
    # Hindi sentence end punctuation: danda(।), ?, !, ., also handling danda with spaces
    sentences = re.split(r'(?<=[।!?\.])\s+', text)
    return [clean_text(s) for s in sentences if s.strip()]

def scrape_text_from_url(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Remove script and style tags
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return text
    except Exception as e:
        return ""

def align_sentences_bidirectional(english_sentences, hindi_sentences, threshold=0.45):
    if not english_sentences or not hindi_sentences:
        return []

    # Filter short sentences (less than 3 words)
    english_sentences = [s for s in english_sentences if len(s.split()) > 2]
    hindi_sentences = [s for s in hindi_sentences if len(s.split()) > 2]

    if not english_sentences or not hindi_sentences:
        return []

    english_embeddings = model.encode(english_sentences, convert_to_tensor=True)
    hindi_embeddings = model.encode(hindi_sentences, convert_to_tensor=True)

    sim_matrix = cosine_similarity(
        english_embeddings.cpu().numpy(),
        hindi_embeddings.cpu().numpy()
    )

    eng_to_hindi = np.argmax(sim_matrix, axis=1)
    hindi_to_eng = np.argmax(sim_matrix, axis=0)

    aligned_pairs = []
    pair_id = 1
    used_eng = set()
    used_hindi = set()

    for eng_idx, hindi_idx in enumerate(eng_to_hindi):
        if hindi_idx >= len(hindi_sentences):
            continue
        if hindi_to_eng[hindi_idx] == eng_idx:
            score = sim_matrix[eng_idx][hindi_idx]
            if score >= threshold:
                if eng_idx not in used_eng and hindi_idx not in used_hindi:
                    aligned_pairs.append({
                        'id': pair_id,
                        'english': english_sentences[eng_idx],
                        'hindi': hindi_sentences[hindi_idx]
                    })
                    used_eng.add(eng_idx)
                    used_hindi.add(hindi_idx)
                    pair_id += 1

    return aligned_pairs

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    english_url = data.get('english_url', '')
    hindi_url = data.get('hindi_url', '')

    if not english_url or not hindi_url:
        return jsonify({'error': 'Both URLs required'})

    eng_text = scrape_text_from_url(english_url)
    hin_text = scrape_text_from_url(hindi_url)

    eng_sentences = split_english_sentences(eng_text)
    hin_sentences = split_hindi_sentences(hin_text)

    return jsonify({
        'english': {'sentences': eng_sentences},
        'hindi': {'sentences': hin_sentences}
    })

@app.route('/align', methods=['POST'])
def align():
    data = request.get_json()
    english_sentences = data.get('english_sentences', [])
    hindi_sentences = data.get('hindi_sentences', [])

    aligned_data = align_sentences_bidirectional(english_sentences, hindi_sentences)

    if not aligned_data:
        return jsonify({'error': 'No aligned sentences found', 'aligned_data': []})

    return jsonify({'aligned_data': aligned_data})

@app.route('/upload-files', methods=['POST'])
def upload_files():
    english_file = request.files.get('english_file')
    hindi_file = request.files.get('hindi_file')

    if not english_file or not hindi_file:
        return jsonify({'error': 'Both files required'})

    eng_text = english_file.read().decode('utf-8')
    hin_text = hindi_file.read().decode('utf-8')

    eng_sentences = split_english_sentences(eng_text)
    hin_sentences = split_hindi_sentences(hin_text)

    aligned_data = align_sentences_bidirectional(eng_sentences, hin_sentences)

    return jsonify({
        'english': {'sentences': eng_sentences},
        'hindi': {'sentences': hin_sentences},
        'aligned_data': aligned_data
    })

if __name__ == '__main__':
    app.run(debug=True)
