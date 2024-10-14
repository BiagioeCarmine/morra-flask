# Pull immagine base
FROM python:3.9-alpine
# Impostazione working directory
WORKDIR /code
# installazione compilatori e header C e C++ per dipendenze app
RUN apk add gcc musl-dev g++ python3-dev linux-headers libffi-dev
# copia del file requirements nel container per installazione dipendenze
COPY requirements.txt requirements.txt
# installazione dipendenze
RUN pip install -r requirements.txt
# suggerimento di aprire porta 5000
EXPOSE 5000
# variabile FLASK_RUN_HOST per non limitare le richieste a cui risponde Flask
ENV FLASK_RUN_HOST=0.0.0.0
# copia del codice dell'app nel container
COPY . .
# impostazione ENTRYPOINT del container
ENTRYPOINT ["python", "-u", "index.py"]
