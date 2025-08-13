FROM PROVIDE PYTHON BASE IMAGE ABOVE 3.9 VERSION
ENV DEBIAN_FRONTEND=noninteractive

COPY . .

RUN pip install -r requirements/requirement.txt
WORKDIR src

CMD ["sh", "-c", "python main.py"]
