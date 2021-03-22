FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc g++ musl-dev linux-headers libffi-dev openssl-dev python3-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_RUN_HOST=0.0.0.0
COPY . .
CMD ["python", "index.py"]