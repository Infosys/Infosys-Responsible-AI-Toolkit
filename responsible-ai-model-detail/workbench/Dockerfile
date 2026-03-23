FROM python:3.9.13
 
ENV DEBIAN_FRONTEND=noninteractive
 
Copy . .
 
RUN pip3 install -r requirements/requirement.txt
WORKDIR src
 
CMD ["sh", "-c", "python3 main.py"]
 
