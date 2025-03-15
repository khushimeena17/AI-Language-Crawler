from laserembeddings import Laser
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize LASER
laser = Laser()

def align_sentences(english_sentences, hindi_sentences):
    aligned_sentences = []
    serial_number = 1

    if not english_sentences or not hindi_sentences:
        return []

    # Generate sentence embeddings
    en_embeddings = laser.embed_sentences(english_sentences, lang='en')
    hi_embeddings = laser.embed_sentences(hindi_sentences, lang='hi')

    # Compute cosine similarity
    similarity_matrix = cosine_similarity(en_embeddings, hi_embeddings)

    # Track matched Hindi sentences to avoid duplicate pairing
    matched_hindi_indices = set()

    for i, en_sentence in enumerate(english_sentences):
        best_match_index = np.argmax(similarity_matrix[i])
        best_match_score = similarity_matrix[i][best_match_index]

        # Ensure unique matches and apply a stricter similarity threshold (e.g., 0.75)
        if best_match_score > 0.75 and best_match_index not in matched_hindi_indices:
            aligned_sentences.append({
                "serial": serial_number,
                "english": en_sentence,
                "hindi": hindi_sentences[best_match_index]
            })
            matched_hindi_indices.add(best_match_index)
            serial_number += 1

    return aligned_sentences