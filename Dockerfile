FROM ubuntu:latest
EXPOSE 80

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev build-essential mariadb-client-10.0 libmysqlclient-dev libapache2-mod-wsgi apache2
RUN rm /etc/apache2/sites-enabled/000-default.conf
COPY ./docker/apache-filmlog.conf /etc/apache2/sites-available/filmlog.conf
RUN ln -s /etc/apache2/sites-available/filmlog.conf /etc/apache2/sites-enabled/filmlog.conf

COPY . /srv/filmlog.org
WORKDIR /srv/filmlog.org
RUN pip install -r requirements.txt
RUN useradd -d /srv/filmlog.org filmlog
RUN chown -R filmlog:www-data /srv/filmlog.org
RUN python setup.py develop
CMD /usr/sbin/apache2ctl -D FOREGROUND
