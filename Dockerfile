FROM python:3.7-slim
ENV APP_HOME /
WORKDIR $APP_HOME
COPY . ./
RUN pip install pipenv
RUN pipenv install --deploy --system
RUN python -m nltk.downloader stopwords
CMD exec web: gunicorn --bind :$PORT --workers 1 --threads 8 app:app