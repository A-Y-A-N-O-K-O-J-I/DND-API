# 1️⃣ Use an official Python image as base
FROM python:3.11-slim

# 2️⃣ Set working directory inside container
WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get install ffmpeg && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/A-Y-A-N-O-K-O-J-I/DND-API /app

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Expose port for Flask
EXPOSE 7860

# 7️⃣ Run the app
CMD ["python", "app.py"]
