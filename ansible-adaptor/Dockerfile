FROM ansible/ansible:ubuntu1604py3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
COPY ansible.cfg /etc/ansible/

EXPOSE 8080
CMD ["python3","-m", "swagger_server"]
