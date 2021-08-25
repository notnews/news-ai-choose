FROM amazon/aws-lambda-python:3.7

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

CMD ["main.handler"]
