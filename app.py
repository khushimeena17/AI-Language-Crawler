from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# Load LaBSE Model for Sentence Alignment
model = SentenceTransformer("sentence-transformers/LaBSE")

# Function to scrape website text
def scrape_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad response
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract only paragraph text (Modify this for better results)
        paragraphs = soup.find_all("p")
        sentences = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
        
        return sentences
    except Exception as e:
        return {"error": f"Failed to fetch data from {url}: {str(e)}"}

# Function to align sentences
def align_sentences(english_sentences, hindi_sentences):
    aligned_pairs = []

    # Compute sentence embeddings
    en_embeddings = model.encode(english_sentences, convert_to_tensor=True)
    hi_embeddings = model.encode(hindi_sentences, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_matrix = util.pytorch_cos_sim(en_embeddings, hi_embeddings)

    for i, en_sentence in enumerate(english_sentences):
        # Find the best matching Hindi sentence
        best_match_index = similarity_matrix[i].argmax().item()
        similarity_score = similarity_matrix[i][best_match_index].item()

        if similarity_score > 0.7:  # Threshold for good alignment
            aligned_pairs.append({
                "id": len(aligned_pairs) + 1,
                "english": en_sentence,
                "hindi": hindi_sentences[best_match_index]
            })

    return aligned_pairs

# Scrape API
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    english_url = data.get("english_url")
    hindi_url = data.get("hindi_url")

    if not english_url or not hindi_url:
        return jsonify({"error": "Both URLs are required!"})

    english_sentences = scrape_text(english_url)
    hindi_sentences = scrape_text(hindi_url)

    if "error" in english_sentences or "error" in hindi_sentences:
        return jsonify({"error": "Failed to fetch data from one or both URLs!"})

    return jsonify({
        "english": {"sentences": english_sentences},
        "hindi": {"sentences": hindi_sentences}
    })

# Align API
@app.route('/align', methods=['POST'])
def align():
    data = request.json
    english_sentences = data.get("english_sentences", [])
    hindi_sentences = data.get("hindi_sentences", [])

    if not english_sentences or not hindi_sentences:
        return jsonify({"error": "Sentences missing!"})

    aligned_data = align_sentences(english_sentences, hindi_sentences)

    return jsonify({"aligned_data": aligned_data})

# Serve HTML file
@app.route('/')
def home():
    return render_template('index.html')
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# Load LaBSE Model for Sentence Alignment
model = SentenceTransformer("sentence-transformers/LaBSE")

# Function to scrape website text
def scrape_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad response
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract only paragraph text (Modify this for better results)
        paragraphs = soup.find_all("p")
        sentences = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
        
        return sentences
    except Exception as e:
        return {"error": f"Failed to fetch data from {url}: {str(e)}"}

# Function to align sentences
def align_sentences(english_sentences, hindi_sentences):
    aligned_pairs = []

    # Compute sentence embeddings
    en_embeddings = model.encode(english_sentences, convert_to_tensor=True)
    hi_embeddings = model.encode(hindi_sentences, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_matrix = util.pytorch_cos_sim(en_embeddings, hi_embeddings)

    for i, en_sentence in enumerate(english_sentences):
        # Find the best matching Hindi sentence
        best_match_index = similarity_matrix[i].argmax().item()
        similarity_score = similarity_matrix[i][best_match_index].item()

        if similarity_score > 0.7:  # Threshold for good alignment
            aligned_pairs.append({
                "id": len(aligned_pairs) + 1,
                "english": en_sentence,
                "hindi": hindi_sentences[best_match_index]
            })

    return aligned_pairs

# Scrape API
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    english_url = data.get("english_url")
    hindi_url = data.get("hindi_url")

    if not english_url or not hindi_url:
        return jsonify({"error": "Both URLs are required!"})

    english_sentences = scrape_text(english_url)
    hindi_sentences = scrape_text(hindi_url)

    if "error" in english_sentences or "error" in hindi_sentences:
        return jsonify({"error": "Failed to fetch data from one or both URLs!"})

    return jsonify({
        "english": {"sentences": english_sentences},
        "hindi": {"sentences": hindi_sentences}
    })

# Align API
@app.route('/align', methods=['POST'])
def align():
    data = request.json
    english_sentences = data.get("english_sentences", [])
    hindi_sentences = data.get("hindi_sentences", [])

    if not english_sentences or not hindi_sentences:
        return jsonify({"error": "Sentences missing!"})

    aligned_data = align_sentences(english_sentences, hindi_sentences)

    return jsonify({"aligned_data": aligned_data})

# Serve HTML file
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
