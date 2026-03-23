FROM infyartifactory.jfrog.io/docker/python:3.9
ENV DEBIAN_FRONTEND=noninteractive

	
COPY . .

RUN pip install -r requirements/requirement.txt 
WORKDIR src

CMD ["sh", "-c", "python main.py"]

