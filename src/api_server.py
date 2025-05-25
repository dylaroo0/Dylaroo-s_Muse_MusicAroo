"""
API Server Plugin
Exposes the AI Music Assistant pipeline as a REST API using FastAPI.
"""
import os
import logging
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from plugin_registry import PLUGINS

# Configure logging
logging.basicConfig(
    filename='logs/api_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="AI Music Assistant API")

@app.on_event("startup")
async def startup_event():
    logging.info("Starting AI Music Assistant API server")
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), plugin_name: str = None) -> Dict:
    """
    Analyzes an uploaded file using the specified plugin or all plugins.

    Args:
        file: Uploaded audio/MIDI/MusicXML file.
        plugin_name: Name of the plugin to run (optional).

    Returns:
        Dict: Analysis results.
    """
    try:
        # Save uploaded file
        file_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logging.info(f"Received file: {file_path}")

        # Determine input type based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".wav"]:
            input_type = "wav"
        elif ext in [".mid", ".midi"]:
            input_type = "midi"
        elif ext in [".musicxml", ".xml"]:
            input_type = "musicxml"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Run plugins
        results = []
        plugins_to_run = [p for p in PLUGINS if p["input_type"] == input_type and (plugin_name is None or p["name"] == plugin_name)]
        if not plugins_to_run:
            raise HTTPException(status_code=400, detail=f"No plugins found for input type {input_type} or plugin name {plugin_name}")

        for plugin in plugins_to_run:
            result = plugin["func"](file_path, output_dir="reports")
            results.append(result)
            logging.info(f"Ran plugin {plugin['name']} on {file_path}: {result}")

        # Clean up
        os.remove(file_path)
        return {"status": "success", "results": results}

    except Exception as e:
        logging.error(f"Error in API analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)