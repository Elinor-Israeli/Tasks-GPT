from unittest.mock import ANY
from unittest.mock import MagicMock, patch
from app.src.vector_store.qdrant_client import get_qdrant_client, _ensure_collection

@patch("app.src.vector_store.qdrant_client.QdrantClient")
def test_get_qdrant_client_creates_collection_if_missing(mock_qdrant_client_class):
    mock_client_instance = MagicMock()
    mock_qdrant_client_class.return_value = mock_client_instance

    mock_client_instance.get_collections.return_value.collections = []

    client = get_qdrant_client(
        host="localhost",
        port=6333,
        collection_name="test_tasks",
        vector_size=384,
        reset=False
    )

    mock_client_instance.get_collections.assert_called_once()
    mock_client_instance.create_collection.assert_called_once_with(
    collection_name="test_tasks",
    vectors_config=ANY
    )
    assert client == mock_client_instance
