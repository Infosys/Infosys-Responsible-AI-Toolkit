FROM python:3.9.13
 
ENV DEBIAN_FRONTEND=noninteractive 
 
COPY . .
# Run a command to display the library path
#RUN find / -path /proc -prune -o \( -name "libQt5Core.so" -o -name "libQt5Core.so.5" \) -print
# Continue with other instructions in the Dockerfile
RUN apt-get update

RUN pip install --upgrade pip
 
RUN pip install -r requirements/requirement.txt 
 
RUN apt-get update && apt-get install -y wkhtmltopdf
 
RUN apt-get update && apt-get install -y libqt5core5a
 
#RUN find / -path /proc -prune -o \( -name "libQt5Core.so" -o -name "libQt5Core.so.5" \) -print
# Continue with other instructions in the Dockerfile
 
RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5
 
WORKDIR src
 
CMD ["sh", "-c", "python3 main.py"]
