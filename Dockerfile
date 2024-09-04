# Important to fix the version of the image
FROM python:3.12.5-alpine3.20

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Host 0.0.0.0 to be able to access the API from outside the container
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
