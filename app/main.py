import os
import time
import threading
import asyncio
import usb.core
import usb.util
from datetime import datetime
from typing import List

from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv

app = FastAPI(title="AIST-IoT Agentic Interface")

# --- Konfigurasi CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

# ==========================================
# BAGIAN 1: ENGINE USB (Tanpa Hardcode ID)
# ==========================================

class USBManager:
    def __init__(self):
        self.device = None
        self.endpoint_in = None
        self.is_reading = False
        self.thread = None
        self.latest_data = None
        self.active_websockets: List[WebSocket] = []

    def find_wifi_dongle(self):
        """
        Mencari perangkat USB berdasarkan keyword, bukan ID statis.
        Mencakup: WLAN, WiFi, 802.11, Wireless, Network.
        """
        print("🔍 Scanning USB bus for generic WiFi dongles...")
        
        # Cari semua perangkat di bus
        devices = usb.core.find(find_all=True)
        
        target_device = None
        
        for dev in devices:
            try:
                # Ambil string deskripsi perangkat
                manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else ""
                product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else ""
                
                combo_name = f"{manufacturer} {product}".lower()
                
                # Cek keyword umum
                keywords = ["wlan", "wifi", "802.11", "wireless", "network", "atheros", "realtek"]
                if any(k in combo_name for k in keywords):
                    print(f"✅ Ditemukan Perangkat Kandidat: {combo_name} (VID: {hex(dev.idVendor)}, PID: {hex(dev.idProduct)})")
                    target_device = dev
                    break # Ambil yang pertama ditemukan
            except Exception as e:
                # Beberapa perangkat memblokir pembacaan string descriptor
                continue

        if target_device is None:
            print("❌ Tidak ada dongle WiFi yang dikenali.")
            return False

        self.device = target_device
        return True

    def setup_connection(self):
        if not self.device:
            return False

        try:
            # 1. Lepaskan kernel driver (Wajib untuk Linux, opsional di Windows via Zadig)
            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                    print("ℹ️ Kernel driver detached.")
                except usb.core.USBError:
                    pass

            # 2. Set Konfigurasi
            self.device.set_configuration()

            # 3. Cari Endpoint IN (Input dari USB ke PC)
            cfg = self.device.get_active_configuration()
            intf = cfg[(0,0)] # Ambil interface pertama
            
            # Loop cari endpoint tipe BULK IN
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.endpoint_in = ep
                    print(f"✅ Endpoint IN ditemukan: {hex(ep.bEndpointAddress)}")
                    break
            
            if not self.endpoint_in:
                print("❌ Tidak ada endpoint IN yang bisa dibaca.")
                return False
                
            return True

        except Exception as e:
            print(f"❌ Error Setup USB: {e}")
            return False

    async def broadcast(self, message: str):
        """Kirim data ke semua browser yang terhubung"""
        for connection in self.active_websockets:
            try:
                await connection.send_text(message)
            except:
                pass

    def read_loop(self):
        """Looping membaca data raw (binary) dari USB"""
        print("🚀 Memulai pembacaan data USB stream...")
        while self.is_reading:
            try:
                if self.endpoint_in:
                    # Baca data (max 64/512 bytes)
                    # Timeout 1000ms agar loop tidak hang
                    data = self.device.read(self.endpoint_in.bEndpointAddress, self.endpoint_in.wMaxPacketSize, timeout=1000)
                    
                    # Konversi Raw Binary ke Hex String agar bisa dibaca manusia
                    hex_data = ''.join([f'{x:02x}' for x in data[:20]]) # Ambil 20 byte pertama saja untuk preview
                    
                    # Buat timestamp
                    ts = datetime.now().strftime("%H:%M:%S")
                    log_msg = f"[{ts}] RAW PACKET: {hex_data}..."
                    
                    print(log_msg) # Print di terminal server
                    
                    # Kirim ke WebSocket (perlu trik karena ini thread biasa ke async)
                    # Kita simpan di variabel, nanti async loop yang broadcast
                    self.latest_data = log_msg
                    
            except usb.core.USBError as e:
                if e.errno == 110: # Timeout (normal jika tidak ada data lewat)
                    continue
                else:
                    print(f"⚠️ USB Error: {e}")
                    break
            except Exception as e:
                print(f"⚠️ Unknown Error: {e}")
                break

    def start_background_reading(self):
        if not self.is_reading:
            self.is_reading = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()

# Inisialisasi Global Manager
usb_manager = USBManager()

# ==========================================
# BAGIAN 2: ROUTING FASTAPI
# ==========================================

class ChatRequest(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    """Jalankan saat server mulai: Cari USB & Mulai Baca"""
    if usb_manager.find_wifi_dongle():
        if usb_manager.setup_connection():
            usb_manager.start_background_reading()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    context = {"request": request, "app_name": "AIST-IoT Hub"}
    return templates.TemplateResponse("index.html", context)

# --- WebSocket Endpoint untuk Real-time Data ---
@app.websocket("/ws/usb")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    usb_manager.active_websockets.append(websocket)
    try:
        while True:
            # Polling sederhana: jika ada data baru di usb_manager, kirim
            if usb_manager.latest_data:
                await websocket.send_text(usb_manager.latest_data)
                usb_manager.latest_data = None # Reset setelah kirim
            await asyncio.sleep(0.1) # Cek setiap 100ms
    except WebSocketDisconnect:
        usb_manager.active_websockets.remove(websocket)

@app.post("/chat")
async def chat_with_ai(chat: ChatRequest):
    user_input = chat.prompt
    # Logika sederhana (Nanti diganti dengan OpenAI/LangChain)
    ai_response = f"Simulasi AI: Saya mendeteksi Anda bertanya tentang '{user_input}'. Status USB: {'Terhubung' if usb_manager.device else 'Terputus'}."
    return {"response": ai_response}

@app.get("/export-log")
async def export_logs():
    filename = "ai_iot_logs.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Event", "Data"])
        writer.writerow([datetime.now(), "System Check", "Exported from AIST-IoT"])
    return FileResponse(path=filename, filename=filename, media_type='text/csv')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)