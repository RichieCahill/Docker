FROM archlinux:latest

WORKDIR /home/r2r0m0c0

COPY etc /etc/

RUN pacman-key --init && \
pacman -Syu --noconfirm && \
pacman -Syu --noconfirm --needed base-devel git curl wget nano neovim tar zsh openssh tmux btop

# RUN pacman -Syu --noconfirm --needed 

COPY ./home .

COPY ./Secret/ /config/Secret
ADD User.sh /config/User.sh
RUN /config/User.sh
RUN cp -r /config/Secret/ssh /etc

RUN git clone https://aur.archlinux.org/yay.git
RUN chown r2r0m0c0:r2r0m0c0 -R /home/r2r0m0c0/
RUN runuser -l r2r0m0c0 -c 'cd /home/r2r0m0c0/yay && makepkg -si --noconfirm'
# RUN runuser -l r2r0m0c0 -c 'yay -Syu --noconfirm'

EXPOSE 22

# CMD service ssh start && tail -f /dev/null
 
CMD /usr/sbin/sshd && tail -f /dev/null
