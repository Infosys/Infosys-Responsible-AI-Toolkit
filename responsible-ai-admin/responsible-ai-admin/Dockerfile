FROM python:3.9.13

RUN useradd myLowPrivilegeUser
USER myLowPrivilegeUser

ENV DEBIAN_FRONTEND=noninteractive

Copy . .

RUN pip3 install -r requirement/requirement.txt

WORKDIR src

CMD ["sh", "-c", "python3 main.py"]

