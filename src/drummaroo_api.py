# drummaroo_api.py
import sys, os

# ─── Make sure `src/` is on PYTHONPATH ─────────────────────────────────────────
ROOT = os.path.dirname(__file__)
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pretty_midi

from drummaroo_plugin import drummaroo
# ────────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DrummAroo API",
    description="Generate drum MIDI for an input clip",
    version="0.1",
)

class GenerateRequest(BaseModel):
    input_path: str   = Field(..., description="Path to source MIDI or WAV on disk")
    out_dir:    str   = Field("reports", description="Where to write drum MIDI")
    style:      str   = Field("post-folk", description="Percussion style")
    swing:      float = Field(0.0, ge=0.0, le=1.0, description="Swing amount 0–1")
    complexity: float = Field(0.5, ge=0.0, le=1.0, description="Rhythmic complexity 0–1")

class Note(BaseModel):
    pitch:    int
    start:    float
    end:      float
    velocity: int

class GenerateResponse(BaseModel):
    status:      str
    output_file: str
    notes:       list[Note]

@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        result = drummaroo(
            input_path=req.input_path,
            out_dir=req.out_dir,
            style=req.style,
            swing=req.swing,
            complexity=req.complexity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DrummAroo error: {e}")

    midi_path = result["output_file"]
    if not os.path.isfile(midi_path):
        raise HTTPException(404, detail=f"Output MIDI not found: {midi_path}")

    pm = pretty_midi.PrettyMIDI(midi_path)
    drums = pm.instruments[0]
    notes = [
        Note(
            pitch=n.pitch,
            start=round(n.start,4),
            end=round(n.end,4),
            velocity=n.velocity
        )
        for n in drums.notes
    ]

    return GenerateResponse(
        status="success",
        output_file=midi_path,
        notes=notes
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("drummaroo_api:app", host="0.0.0.0", port=8000, reload=True)
