FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY calculators/ ./calculators/
COPY exporters/ ./exporters/
COPY persistence/ ./persistence/
COPY assets/ ./assets/

EXPOSE 8000

CMD ["python", "server.py"]
