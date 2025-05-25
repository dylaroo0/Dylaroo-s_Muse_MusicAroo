def test_audio_analysis_endpoint(client, sample_wav_path):
    with open(sample_wav_path, "rb") as f:
        response = client.post("/analyze/audio", files={"file": f})
    assert response.status_code == 200
    assert "tempo_bpm" in response.json()

def test_midi_analysis_endpoint(client, sample_midi_path):
    with open(sample_midi_path, "rb") as f:
        response = client.post("/analyze/midi", files={"file": f})
    assert response.status_code == 200
    assert "phrases" in response.json()

def test_tab_generation_endpoint(client):
    data = {"chords": ["C", "Am", "F", "G"]}
    response = client.post("/generate/tab", json=data)
    assert response.status_code == 200
    assert "e|" in response.json()["tab"]
