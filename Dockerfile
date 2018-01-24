FROM ubuntu:latest
EXPOSE 80

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential mariadb-client-10.0 libmysqlclient-dev

# This requires multiple dockers, one for the app, one for nginx
# RUN apt-get install -y nginx uwsgi-plugin-python uwsgi
#COPY ./docker/nginx-filmlog.conf /etc/nginx/sites-enabled/filmlog.conf
#COPY ./docker/filmlog.conf /etc/init
# RUN rm /etc/nginx/sites-enabled/default

# This is a cheaty all in one
RUN apt-get install -y libapache2-mod-wsgi apache2
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

# Old
#CMD ["nginx", "-g", "daemon off;"]
# RUN . venv/bin/activate
#CMD ./wsgi.sh
#EXPOSE 5000
#ENTRYPOINT ./wsgi.sh
#WORKDIR /app/filmlog
#ENV FLASK_APP filmlog
#RUN flask run
#ENTRYPOINT ["python"]
#CMD ["__init__.py"]
