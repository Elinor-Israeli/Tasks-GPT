from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, model_name = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()    

# Load a sentence-transformers model.
# Provides a function to convert a string (like task title) to a vector.
# TODO: this TextEmbedder is from open-source i will need to check if its good