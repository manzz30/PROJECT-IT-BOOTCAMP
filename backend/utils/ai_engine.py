import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

def parse_embedding(embedding_str: str) -> np.ndarray:
    """Convert JSON string to numpy array"""
    arr = json.loads(embedding_str)
    return np.array(arr)

def verify_face(input_embedding: str, db_embeddings: list) -> dict:
    """
    Mencocokkan wajah input dengan database
    Return: {matched: bool, user: dict, confidence: float}
    """
    input_emb = parse_embedding(input_embedding)
    
    best_match = None
    best_score = 0.0
    
    for user in db_embeddings:
        stored_emb = parse_embedding(user["face_embedding"])
        # Calculate cosine similarity
        score = cosine_similarity([input_emb], [stored_emb])[0][0]
        
        if score > best_score:
            best_score = score
            best_match = user
    
    # Threshold 70%
    threshold = 0.70
    return {
        "matched": best_score >= threshold,
        "user": best_match,
        "confidence": float(best_score)
    }

def calculate_liveness_score(face_data: dict) -> float:
    """
    Placeholder untuk liveness detection
    Di production: gunakan model CNN atau library seperti DeepFace
    """
    # Simulasi score berdasarkan confidence
    if face_data.get("confidence", 0) > 0.85:
        return 0.92
    return 0.50