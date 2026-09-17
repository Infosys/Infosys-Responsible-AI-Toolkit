FROM python:3.9.13
ENV DEBIAN_FRONTEND=noninteractive


COPY . .

RUN pip install -r requirements/requirements.txt
WORKDIR src

CMD ["sh", "-c", "python main.py"]

