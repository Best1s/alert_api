FROM python
MAINTAINER zhangbin
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
COPY ["app.py","/"]
COPY ["code","/"]
COPY ["myjsonpath.py","/"]
COPY ["natapi.py","/"]
WORKDIR /
RUN  pip install flask  tencentcloud-sdk-python requests -i https://pypi.douban.com/simple
EXPOSE 5000
CMD python app.py
