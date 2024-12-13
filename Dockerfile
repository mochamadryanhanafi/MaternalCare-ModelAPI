# Gunakan image Python 3.8 sebagai base image
FROM python:3.8-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt dan instal dependensi
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi Flask ke dalam container
COPY . .


# Expose port 8080
EXPOSE 8080

# Jalankan aplikasi Flask di host 0.0.0.0 untuk mengizinkan akses dari luar container
CMD ["python", "app.py"]
