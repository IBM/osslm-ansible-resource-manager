FROM ansible/ansible:ubuntu1604py3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
COPY ansible.cfg /etc/ansible/
COPY tslvault.txt /etc/ansible/
COPY ans_alm_settings.yml /etc/ansible/

# device handling
RUN pip3 install --no-cache-dir -r device-requirements.txt

# using ansible 2.6 juniper core modules
#RUN ansible-galaxy install Juniper.junos
# fixes a bug in the junos libs (for python3)
#COPY junos_install_config /etc/ansible/roles/Juniper.junos/library/.
#COPY junos_get_config /etc/ansible/roles/Juniper.junos/library/.

# multi python process handling
RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080 
CMD ["/usr/bin/supervisord"]
#CMD ["python3","-m", "swagger_server"]
