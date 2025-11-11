FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# initialize DB when container starts if not exists
CMD ["sh", "-c", "python init_db.py && python app.py"]
