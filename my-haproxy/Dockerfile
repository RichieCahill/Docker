FROM haproxy:latest

WORKDIR /

ADD haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

ADD cloudflare.pem /etc/ssl/certs/cloudflare.pem

EXPOSE 80
EXPOSE 443

CMD haproxy -f /usr/local/etc/haproxy/haproxy.cfg
