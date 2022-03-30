FROM debian:11

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /root

RUN echo "Updating" && \
apt update && apt upgrade -y

RUN echo "installing pacages" && \
apt install -y zsh iputils-ping iproute2 zsh less curl wget \
git nano neovim smartmontools apt-transport-https htop tmux

COPY ./home .

# RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

CMD tail -f /dev/null