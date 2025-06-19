import pytest
from unittest.mock import MagicMock, patch
from app.src.vector_store.qdrant_client import get_qdrant_client, _ensure_collection


@pytest.fixture
def mock_qdrant_client():
    client = MagicMock()
    client.get_collections.return_value.collections = []
    return client


def test_ensure_collection_creates_if_not_exists(mock_qdrant_client):
    _ensure_collection(mock_qdrant_client, collection_name="my_tasks", vector_size=384, reset=False)

    mock_qdrant_client.create_collection.assert_called_once_with(
        collection_name="my_tasks",
        vectors_config=mock_qdrant_client.create_collection.call_args[1]["vectors_config"]
    )


def test_get_qdrant_client_calls_ensure_collection():
    with patch("vector_store.qdrant_client._ensure_collection") as mock_ensure, \
         patch("vector_store.qdrant_client.QdrantClient") as mock_client_class:

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = get_qdrant_client(collection_name="tasks_test", vector_size=128)

        mock_ensure.assert_called_once_with(mock_client, "tasks_test", 128, False)
        assert client == mock_client
