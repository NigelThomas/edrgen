FROM python:3-alpine

RUN apk update && apk add kafkacat

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY run_generator.sh .
COPY datagen.py .
COPY model_files.tgz .
COPY run_generator.sh .
COPY kafka.config .
CMD ["python", "run_generator.py"]
