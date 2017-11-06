FROM ansible/ansible:ubuntu1604py3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
COPY ansible.cfg /etc/ansible/

RUN ansible-galaxy install Juniper.junos
# fixes a bug in the junos libs (for python3)
COPY junos_install_config /etc/ansible/roles/Juniper.junos/library/.

EXPOSE 8080
CMD ["python3","-m", "swagger_server"]
