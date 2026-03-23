FROM python:3.9.13
ENV DEBIAN_FRONTEND=noninteractive

COPY . .
RUN pip install -r requirements/requirement.txt
ENV http_proxy=
ENV https_proxy=
WORKDIR src
CMD ["sh", "-c", "python main_api.py"]
