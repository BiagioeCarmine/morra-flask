FROM python:3.9-alpine
WORKDIR /code
RUN apk add gcc musl-dev g++ python3-dev linux-headers libffi-dev
RUN wget https://raw.githubusercontent.com/eficode/wait-for/v2.1.0/wait-for
RUN chmod +x wait-for
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0
COPY . .
ENTRYPOINT ["./wait-for", "mysql:3306", "--", "python", "-u", "index.py"]
