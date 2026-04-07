FROM FROM python:3.9.13
 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y wkhtmltopdf
 
COPY . .
 
RUN pip install --upgrade pip
 
RUN pip install -r requirements/requirement.txt 

WORKDIR app

CMD ["sh", "-c", "python3 main.py"]
