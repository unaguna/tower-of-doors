FROM python:3.10.4

RUN apt update
RUN apt install -y default-mysql-client-core

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install mysqlclient==2.1.*

RUN ln -s /var/lib/db-update/scripts/tod.sh /usr/local/bin/tod

COPY ./scripts/ /var/lib/db-update/scripts

ENTRYPOINT ["python", "/var/lib/db-update/scripts/tod-bg.py"]
