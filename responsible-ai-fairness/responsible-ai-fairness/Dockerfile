FROM python:3.9.13
ENV DEBIAN_FRONTEND=noninteractive

ENV ACCESS_KEY= 
ENV SECRET_KEY= 
	
COPY . .

RUN pip install -r requirements/requirement.txt 
WORKDIR src

CMD ["sh", "-c", "python main_api.py"]
