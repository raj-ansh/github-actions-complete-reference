# syntax=docker/dockerfile:1
FROM python:3.14-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.14-slim
RUN useradd --create-home --uid 10001 shelfwise \
    && mkdir /data && chown shelfwise /data
COPY --from=build /install /usr/local
USER shelfwise
ENV SHELFWISE_DB=/data/shelfwise.db
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD \
    ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health')"]
CMD ["uvicorn", "shelfwise.main:app", "--host", "0.0.0.0", "--port", "8000"]
