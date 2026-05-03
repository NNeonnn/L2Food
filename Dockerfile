FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# Для дебага
RUN pip install debugpy
EXPOSE 5237 5678
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "app.py"]
