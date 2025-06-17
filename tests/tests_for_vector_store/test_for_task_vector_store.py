import pytest
from unittest.mock import MagicMock
from vector_store.task_vector_store import TaskVectorStore


@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    embedder.embed.return_value = [0.1, 0.2, 0.3]
    return embedder

@pytest.fixture
def mock_qdrant_client():
    return MagicMock()

@pytest.fixture
def vector_store(mock_qdrant_client, mock_embedder):
    return TaskVectorStore(client=mock_qdrant_client, embedder=mock_embedder, collection_name="test_tasks")


def test_add_vector(vector_store, mock_qdrant_client):
    vector_store.add(task_id=1, title="Buy milk", user_id=123)
    
    assert mock_qdrant_client.upsert.called
    args, kwargs = mock_qdrant_client.upsert.call_args
    assert kwargs["collection_name"] == "test_tasks"
    assert isinstance(kwargs["points"], list)
    assert kwargs["points"][0].payload["title"] == "Buy milk"


def test_search_vector(vector_store, mock_qdrant_client):
    mock_qdrant_client.search.return_value = ["mock_result_1", "mock_result_2"]

    results = vector_store.search(query="Buy milk", user_id=123, top_k=2)

    assert mock_qdrant_client.search.called
    assert results == ["mock_result_1", "mock_result_2"]


def test_remove_vector(vector_store, mock_qdrant_client):
    vector_store.remove(task_id=1, user_id=123)

    assert mock_qdrant_client.delete.called
    args, kwargs = mock_qdrant_client.delete.call_args
    assert kwargs["collection_name"] == "test_tasks"
    assert kwargs["points_selector"] is not None
