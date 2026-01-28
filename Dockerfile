# Gunakan base image Python yang ringan
FROM python:3.10-slim

# Set folder kerja di dalam container
WORKDIR /app

# Salin requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode dari laptop ke container
COPY . .

# Perintah menjalankan aplikasi (Uvicorn)
# app.main:app artinya -> file app/main.py, object app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]