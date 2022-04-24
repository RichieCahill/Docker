FROM debian:11

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /config

RUN echo "Updating" && apt update && apt upgrade -y

RUN echo "installing pacages" && apt install -y apache2 w3m

ADD 000-default.conf /etc/apache2/sites-enabled/000-default.conf

ENV PORT=80

EXPOSE 80

RUN echo "ServerName 127.0.0.1" >> /etc/apache2/apache2.conf
 
CMD /usr/sbin/apachectl -D FOREGROUND

