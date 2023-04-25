FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE studreply.settings
RUN mkdir -p /usr/src/app/

COPY requirements.txt /usr/src/app/requirements.txt

WORKDIR /usr/src/app/

RUN pip install -r requirements.txt

COPY . /usr/src/app/
ENTRYPOINT ["./manage.py"]