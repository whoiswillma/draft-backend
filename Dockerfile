FROM python:3.7

RUN mkdir -p /usr/draft-backend/src
WORKDIR /usr/draft-backend/src

COPY . .

RUN pip install -r src/requirements.txt

CMD python src/app.py
