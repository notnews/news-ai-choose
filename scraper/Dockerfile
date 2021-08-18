FROM python:3.7

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
  && unzip awscliv2.zip \
  && ./aws/install

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN mkdir -p /app/json_data

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]
