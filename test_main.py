from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)


def test_health_check():
    """
    Test the health check endpoint ("/") to ensure
    the API is responding with 200 OK and the correct message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running."}
