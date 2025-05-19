from flask import Flask, request, jsonify, render_template, send_file
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import re
import csv
import io

app = Flask(__name__)

# Load LaBSE model once
model = SentenceTransformer("sentence-transformers/LaBSE")

# --- Utility Functions ---

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def split_english_sentences(text):
    return [clean_text(s) for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def split_hindi_sentences(text):
    return [clean_text(s) for s in re.split(r'[|।!?]+', text) if s.strip()]

def scrape_text_from_url(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for tag in soup(['script', 'style']):
            tag.extract()
        return soup.get_text(separator=' ')
    except Exception as e:
        return ""

def align_sentences_bidirectional(english_sentences, hindi_sentences, threshold=0.45):
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    english_sentences = [s for s in english_sentences if len(s.split()) > 2]
    hindi_sentences = [s for s in hindi_sentences if len(s.split()) > 2]

    if not english_sentences or not hindi_sentences:
        return []

    english_embeddings = model.encode(english_sentences, convert_to_tensor=True)
    hindi_embeddings = model.encode(hindi_sentences, convert_to_tensor=True)

    sim_matrix = cosine_similarity(english_embeddings.cpu().numpy(), hindi_embeddings.cpu().numpy())

    eng_to_hin = np.argmax(sim_matrix, axis=1)
    hin_to_eng = np.argmax(sim_matrix, axis=0)

    aligned = []
    used_eng, used_hin = set(), set()
    pair_id = 1

    for eng_idx, hin_idx in enumerate(eng_to_hin):
        if hin_idx < len(hindi_sentences) and hin_to_eng[hin_idx] == eng_idx:
            score = sim_matrix[eng_idx][hin_idx]
            if score >= threshold and eng_idx not in used_eng and hin_idx not in used_hin:
                aligned.append({
                    'id': pair_id,
                    'english': english_sentences[eng_idx],
                    'hindi': hindi_sentences[hin_idx]
                })
                used_eng.add(eng_idx)
                used_hin.add(hin_idx)
                pair_id += 1
    return aligned

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    en_url, hi_url = data.get('english_url'), data.get('hindi_url')

    if not en_url or not hi_url:
        return jsonify({'error': 'Both URLs are required'}), 400

    en_text = scrape_text_from_url(en_url)
    hi_text = scrape_text_from_url(hi_url)

    return jsonify({
        'english': {'sentences': split_english_sentences(en_text)},
        'hindi': {'sentences': split_hindi_sentences(hi_text)}
    })

@app.route('/align', methods=['POST'])
def align():
    data = request.get_json()
    en_sentences = data.get('english_sentences', [])
    hi_sentences = data.get('hindi_sentences', [])
    aligned = align_sentences_bidirectional(en_sentences, hi_sentences)
    return jsonify({'aligned_data': aligned})

@app.route('/upload-files', methods=['POST'])
def upload_files():
    en_file = request.files.get('english_file')
    hi_file = request.files.get('hindi_file')

    if not en_file or not hi_file:
        return jsonify({'error': 'Both files are required'}), 400

    en_text = en_file.read().decode('utf-8')
    hi_text = hi_file.read().decode('utf-8')

    en_sentences = split_english_sentences(en_text)
    hi_sentences = split_hindi_sentences(hi_text)

    aligned = align_sentences_bidirectional(en_sentences, hi_sentences)
    return jsonify({
        'english': {'sentences': en_sentences},
        'hindi': {'sentences': hi_sentences},
        'aligned_data': aligned
    })

@app.route('/download_csv', methods=['POST'])
def download_csv():
    data = request.get_json()
    aligned_data = data.get('aligned_data', [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Serial No.', 'English Sentence', 'Hindi Sentence'])
    for row in aligned_data:
        writer.writerow([row['id'], row['english'], row['hindi']])
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='aligned_sentences.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
