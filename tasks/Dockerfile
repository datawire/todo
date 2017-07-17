# Run server
FROM alpine:3.5
RUN apk add --no-cache python py2-pip py2-gevent
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app.py"]
