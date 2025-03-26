FROM public.ecr.aws/lambda/python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /var/task
COPY . .

RUN python -m pip install -r requirements.txt

EXPOSE 9000
CMD ["lambda_function.lambda_handler"]
