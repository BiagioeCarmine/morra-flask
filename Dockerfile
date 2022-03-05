FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc g++ musl-dev linux-headers libffi-dev openssl-dev python3-dev
RUN wget https://raw.githubusercontent.com/eficode/wait-for/v2.1.0/wait-for
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0
COPY . .
ENTRYPOINT ["./wait-for", "mysql:3306", "--", "python", "-u", "index.py"]
