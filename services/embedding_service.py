from sentence_transformers import SentenceTransformer

# Load S-BERT model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):
    """
    Generate a semantic embedding for the given text using S-BERT.
    """
    embedding = model.encode(text)
    return embedding