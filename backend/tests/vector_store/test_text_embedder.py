from app.vector_store.text_embedder import TextEmbedder

def test_text_embedder_returns_embedding_vector():
    embedder = TextEmbedder()
    text = "This is a test sentence."
    embedding = embedder.embed(text)

    assert isinstance(embedding, list)
    assert all(isinstance(value, float) for value in embedding)
    assert len(embedding) > 0  