FROM python:3.10.4

ENV PYTHONUNBUFFERED 1
ENV PRODUCTION 1
ENV DJANGO_SECRET_KEY 1
ENV SQL_ENGINE django.db.backends.postgresql
ENV DB_NAME lime
ENV DB_USER lime
ENV DB_PASSWORD lime
ENV DB_HOST db
ENV DB_PORT 5432
ENV CELERY_BROKER_URL redis://localhost/
ENV DJANGO_DEBUG 1
ENV V Docerfile


RUN apt-get update && apt-get -y install uuid-dev python3-xapian python3-dev graphviz libgraphviz-dev pkg-config

RUN curl -O https://oligarchy.co.uk/xapian/1.4.19/xapian-core-1.4.19.tar.xz \
    && tar -xvf xapian-core-1.4.19.tar.xz \
    && cd xapian-core-1.4.19 && ./configure && make && make install
RUN curl -O https://oligarchy.co.uk/xapian/1.4.19/xapian-bindings-1.4.19.tar.xz \
    && tar -xvf xapian-bindings-1.4.19.tar.xz \
    && cd xapian-bindings-1.4.19 && ./configure && make && make install
RUN rm -rf xapian-*

RUN mkdir /code
WORKDIR /code

COPY . /code
#ADD ./requirements.txt /code/
RUN ls -la /code

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt