from laserembeddings import Laser
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize LASER model
laser = Laser()

def align_sentences(english_sentences, hindi_sentences):
    """
    Aligns English sentences with their correct Hindi translations.

    Args:
    - english_sentences (list): List of extracted English sentences.
    - hindi_sentences (list): List of extracted Hindi sentences.

    Returns:
    - aligned_sentences (list): List of tuples (serial_no, English, Hindi).
    """
    aligned_sentences = []
    
    # Embed the sentences using LASER
    eng_embeddings = laser.embed_sentences(english_sentences, lang='en')
    hin_embeddings = laser.embed_sentences(hindi_sentences, lang='hi')

    # Iterate through each English sentence embedding
    for i, eng_embedding in enumerate(eng_embeddings):
        # Calculate cosine similarities with all Hindi embeddings
        similarities = cosine_similarity([eng_embedding], hin_embeddings)[0]
        
        # Find the index of the maximum similarity score
        max_sim_index = np.argmax(similarities)
        max_sim_score = similarities[max_sim_index]

        # Check if the maximum similarity score exceeds the threshold
        if max_sim_score > 0.7:  # Adjust threshold as needed
            aligned_sentences.append((len(aligned_sentences) + 1, english_sentences[i], hindi_sentences[max_sim_index]))

    return aligned_sentences