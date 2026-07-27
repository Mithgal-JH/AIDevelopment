from app.main import create_app

def test_generate_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.post("/generate", json={
        "text": "Artificial intelligence is changing the world."
    })

    assert response.status_code == 200
    assert "result" in response.json
