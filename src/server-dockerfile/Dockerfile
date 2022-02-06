FROM python:3-alpine

RUN pip install pymongo flask

WORKDIR /app

COPY /src .

CMD [ "python", "./server.py" ]
