FROM python
MAINTAINER zhangbin
COPY ["app.py","/"]
COPY ["code","/"]
ADD ["templates/","/templates"]
WORKDIR /
RUN  pip install flask requests -i https://pypi.douban.com/simple
EXPOSE 5000
CMD python app.py 
