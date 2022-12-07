FROM python:latest

WORKDIR /app

# install dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy scripts to the src folder
COPY . /app

# start a server
CMD []