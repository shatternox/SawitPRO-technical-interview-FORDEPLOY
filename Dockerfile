FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    libmariadb-dev-compat \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV PKG_CONFIG_PATH /usr/lib/x86_64-linux-gnu/pkgconfig

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py

ENV FLASK_SECRET_KEY=4528f440-1791-4770-b153-73dae6de7f73

ENV MYSQL_HOST=db
ENV MYSQL_USER=sawidproadmin
ENV MYSQL_PASSWORD=vaeiiGbL%j3jjQ!6duFKk79koKYLch%d
ENV MYSQL_DB=sawitpro

EXPOSE 6969

# CMD ["flask", "run", "--host", "0.0.0.0", "--port", "6969", "--debug"]
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "6969"]
