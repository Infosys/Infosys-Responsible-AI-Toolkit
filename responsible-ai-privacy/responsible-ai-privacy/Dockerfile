FROM python:3.11-slim

RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup appuser

ENV DEBIAN_FRONTEND=noninteractive

COPY . .

RUN pip3 install -r requirements/requirement.txt

WORKDIR /src

USER 10001:10001

CMD ["python3","main.py"]