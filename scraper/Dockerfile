FROM amazon/aws-cli:latest

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN mkdir -p /app/json_data

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]
