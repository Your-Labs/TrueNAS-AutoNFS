ARG PYTHON_VERSION=3.12-alpine

FROM python:${PYTHON_VERSION} AS builder
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

FROM python:${PYTHON_VERSION}
WORKDIR /app
USER daemon
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
ENTRYPOINT [ "python", "/app/app.py" ]
CMD [ "--config", "/app/config.json" ]