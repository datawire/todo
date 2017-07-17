# Run server
FROM alpine:3.5
RUN apk add --no-cache autoconf g++ python python-dev py2-pip py2-gevent ca-certificates && update-ca-certificates
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app.py"]
