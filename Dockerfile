FROM python:3.7-slim
ENV APP_HOME /
WORKDIR $APP_HOME
COPY . ./
RUN pip3 install pipenv==2018.11.26 
RUN pipenv install --deploy --system
RUN python -m nltk.downloader all -d /usr/local/nltk_data
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app