FROM archlinux:latest

WORKDIR /home/r2r0m0c0

COPY etc /etc/

RUN pacman-key --init && \
pacman -Syu --noconfirm && \
pacman -S --noconfirm --needed base base-devel git curl wget nano neovim tar zsh openssh tmux btop

# RUN pacman -S --noconfirm --needed cuda
# RUN pacman -S --noconfirm --needed nvidia cuda
 
# configure nvidia container runtime
# https://github.com/NVIDIA/nvidia-container-runtime#environment-variables-oci-spec
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

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
RUN runuser -l r2r0m0c0 -c 'yay -S --noconfirm nvidia-470xx-dkms'
RUN pacman -S --noconfirm --needed ffmpeg

EXPOSE 22

# CMD service ssh start && tail -f /dev/null
 
CMD /usr/sbin/sshd && tail -f /dev/null
