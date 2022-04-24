FROM haproxy:latest

WORKDIR /

ADD haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

EXPOSE 80
EXPOSE 443

CMD haproxy -f /usr/local/etc/haproxy/haproxy.cfg

# haproxy -f /usr/local/etc/haproxy/haproxy.cfg

