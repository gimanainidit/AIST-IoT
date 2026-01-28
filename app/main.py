import os
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv

# --- 1. Import Logika Lama (Simulasi Integrasi) ---
# Di masa depan, kamu akan mengimport class/fungsi asli dari repo AIST-IoT di sini.
# from iot_service import MQTTClient, SensorReader 

app = FastAPI(title="AIST-IoT Agentic Interface")

# --- 2. Konfigurasi CORS & Templates ---
# Penting agar browser bisa kirim data sensor via Fetch API tanpa diblokir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DI PRODUCTION< GANTI DENGAN DOMAIN ASLI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

# --- 3. Model Data (Pydantic) ---
class ChatRequest(BaseModel):
    prompt: str

class SensorData(BaseModel):
    sensor_value: str
    timestamp: str = datetime.now().isoformat()

# --- 4. Routes / Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Menampilkan UI Microsite Linktree"""
    # Kita kirim data menu dinamis ke HTML
    context = {"request": request, "app_name": "AIST-IoT Hub"}
    return templates.TemplateResponse("index.html", context)

@app.post("/process-sensor")
async def receive_sensor_data(data: SensorData, background_tasks: BackgroundTasks):
    """
    Endpoint ini menerima data dari Hardware (USB) yang dikirim oleh Browser.
    """
    print(f"📡 Data Diterima dari Hardware: {data.sensor_value}")
    
    # [Roadmap Fase 2]: Di sini nanti kita masukkan logika RAG/Vector DB
    # background_tasks.add_task(save_to_vector_db, data.sensor_value)
    
    # [Roadmap Fase 3]: Di sini Agent AI mengevaluasi data
    # analysis = ai_agent.analyze(data.sensor_value)
    
    return {"status": "success", "message": "Data processed by AI Core"}

@app.post("/chat")
async def chat_with_ai(chat: ChatRequest):
    """
    Simulasi Chatbot AI (LangChain Placeholder)
    """
    user_input = chat.prompt
    
    # Logika sederhana (Nanti diganti dengan OpenAI/LangChain)
    ai_response = f"Saya menerima perintah: '{user_input}'. (Mode Agentic belum aktif sepenuhnya)"
    
    return {"response": ai_response}

@app.get("/export-log")
async def export_logs():
    """
    Fitur Export Log ke CSV
    """
    filename = "ai_iot_logs.csv"
    
    # Membuat file dummy log
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Event", "Data"])
        writer.writerow([datetime.now(), "Sensor Reading", "32.5 C"])
        writer.writerow([datetime.now(), "AI Interaction", "User asked about status"])
        
    return FileResponse(path=filename, filename=filename, media_type='text/csv')

# --- 5. Entry Point untuk Debugging Lokal ---
if __name__ == "__main__":
    import uvicorn
    # Jalankan server: localhost port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)