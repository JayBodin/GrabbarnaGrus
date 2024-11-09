# Välj en basimage för att köra Python
FROM python:3.x

# Sätt arbetskatalogen i containern
WORKDIR /app

# Kopiera din applikations filer till arbetskatalogen
COPY . /app

# Installera beroenden som definieras i requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ange kommandot för att köra applikationen (ersätt med din huvudfil, t.ex. app.py)
CMD ["python", "app.py"]
