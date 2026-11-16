# DataSage browser app in one container.
#   docker build -t datasage .
#   docker run --rm -p 8501:8501 --env-file .env datasage      # then open http://127.0.0.1:8501
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY datasage/ datasage/
COPY app/ app/
COPY examples/ examples/
COPY baseline/examples/ baseline/examples/

RUN useradd --create-home datasage && mkdir -p outputs && chown datasage outputs
USER datasage
EXPOSE 8501
# 0.0.0.0 inside the container; docker run -p 8501:8501 still only publishes it on this machine's port.
CMD ["python", "-m", "app.web.server", "--host", "0.0.0.0", "--port", "8501"]
