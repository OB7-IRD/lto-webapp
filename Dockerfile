# base image  
FROM python:3.13-bullseye
# setup environment variable  
ENV DockerHOME=/home/app/webapp  

# set work directory  
RUN mkdir -p /var/www/static/
RUN mkdir -p /var/www/lto-webapp/static/
RUN mkdir -p $DockerHOME/static  
RUN mkdir -p $DockerHOME/database  
RUN mkdir -p $DockerHOME/media/data  

# where your code lives  
WORKDIR $DockerHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1  

# Update image
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install nano

# install dependencies  
RUN pip install --upgrade pip  

# copy whole project to your docker home directory. 
COPY . $DockerHOME  
# run this command to install all dependencies  
RUN pip install -r requirements.txt  
