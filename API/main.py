from fastapi import FastAPI, UploadFile, File
import tempfile
import sys,os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflow import PhysioSOAPAgent

app = FastAPI()

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(await file.read())
        temp_audio_path = temp_audio.name

    agent = PhysioSOAPAgent()
    result = await agent.process_audio_to_soap(audio_path=temp_audio_path)

    return {
        "status": "success",
        "patient_name": result["soap_model"].patient_name,
        "session_date": result["soap_model"].session_date,
        "soap": result["soap_model"].model_dump(), #.dict(),  # You may need to implement `dict()` in SoapModel
        "markdown_path": result["markdown_path"]
    }
