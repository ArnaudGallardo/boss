FROM ubuntu:18.04

RUN apt-get update && apt-get install -y git python3 python3-pip libmysqlclient-dev lsb-release build-essential libssl-dev

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# RUN pip3 install setuptools wheel

ADD . /boss

# Install bossutils
RUN mkdir /bosstools
WORKDIR /bosstools
RUN git clone https://github.com/jhuapl-boss/boss-tools.git .
# TODO use version arg
RUN git checkout v1.0.6
RUN mv /boss/bossutils.setup.py setup.py
RUN python3 setup.py sdist bdist_wheel
# TODO use arg
RUN pip3 install dist/bossutils-1.0.6-py3-none-any.whl


WORKDIR /boss
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "django/manage.py", "mysql" ]
