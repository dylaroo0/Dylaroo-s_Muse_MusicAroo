# setup.py

from setuptools import setup, find_packages

setup(
    name="ai_music_assistant",
    version="0.1.0",
    description="Modular AI-powered pipeline for audio analysis, transcription, and generation",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "soundfile>=0.10.3.post1",
        "librosa>=0.11.0",
        "pyloudnorm>=0.1.1",
        "crepe>=0.0.16",
        "parselmouth>=0.4.0",
        "musicnn>=0.1.0",
        "pretty_midi>=0.2.10",
        "music21>=8.1.0",
        "note_seq>=0.0.3",
        "demucs>=3.0.0",
        "basic_pitch>=0.1.5",
        "textblob>=0.15.3",
        "openai>=0.27.0",
        "whisperx>=1.3.0",
        "matplotlib>=3.5.0",
        "rich>=12.6.0"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ai-music-assistant=main:run_pipeline",
            "list-plugins=list_plugins:list_plugins_by_phase",
            "list-stages=list_stages:summarize_stages"
        ]
    }
)
