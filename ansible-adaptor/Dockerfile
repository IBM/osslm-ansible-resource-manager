FROM python:3.6-slim-buster

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
COPY device-requirements.txt /usr/src/app/

RUN apt-get update && apt-get install -y supervisor && \
    apt-get install --reinstall -y build-essential && \
    pip3 install --no-cache-dir -r requirements.txt && \
    # device handling
    pip3 install --no-cache-dir -r device-requirements.txt && \
    # using ansible 2.6 juniper core modules + opt juniper role
#    ansible-galaxy install Juniper.junos && \
    mkdir -p /var/log/supervisor

COPY . /usr/src/app
COPY ansible.cfg /etc/ansible/
COPY tslvault.txt /etc/ansible/
COPY ans_alm_settings.yml /etc/ansible/

# multi python process handling
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080
EXPOSE 8443
CMD ["/usr/bin/supervisord"]
