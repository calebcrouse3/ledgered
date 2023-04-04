FROM python:3.9-alpine
EXPOSE 8000
WORKDIR /ledgered
COPY requirements.txt /ledgered
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /ledgered
ENTRYPOINT ["python3"]
CMD [ "manage.py", "runserver", "0.0.0.0:8000"]
