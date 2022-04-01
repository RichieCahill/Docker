FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /home/r2r0m0c0

RUN echo "Updating" && \
apt update && apt upgrade -y

RUN echo "installing pacages" && \
apt install -y zsh iputils-ping iproute2 less curl wget \
git nano neovim smartmontools apt-transport-https htop tmux ssh sudo

ADD User.sh /config/User.sh

COPY ./home .

COPY ./Secret/ /config/Secret

ADD User.sh /config/User.sh

RUN /config/User.sh

RUN cp -r /config/Secret/ssh /etc/ssh

EXPOSE 22

CMD service ssh start && tail -f /dev/null