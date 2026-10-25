FROM python:3.13.12-slim-bookworm@sha256:a58daefb915e1e03ad48f3ca4df8832065412c5c35cacb9d39f4229184de12b6
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY labs/week_12/requirements.txt ./labs/week_12/requirements.txt
RUN python -m pip install --no-cache-dir -r labs/week_12/requirements.txt
COPY labs/week_07 ./labs/week_07
COPY labs/week_08 ./labs/week_08
COPY labs/week_11 ./labs/week_11
COPY labs/week_12 ./labs/week_12
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=6 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready',timeout=4).read()"]
CMD ["python", "-m", "uvicorn", "labs.week_12.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "16", "--timeout-graceful-shutdown", "10", "--no-access-log"]
