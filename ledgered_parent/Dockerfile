FROM python:3.9
EXPOSE 8000
WORKDIR /ledgered_parent
RUN python -m pip install --upgrade pip
COPY requirements.txt /ledgered_parent
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /ledgered_parent
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]