FROM python:3.6.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/ ./src/

EXPOSE 5000
CMD [ "python", "src/" ]