FROM python:3.7-slim
ENV APP_HOME /
WORKDIR $APP_HOME
COPY . ./
RUN pip3 install pipenv==2018.11.26 
RUN pipenv install --deploy --system
RUN pip install nltk
RUN python -m nltk.downloader -d /usr/local/nltk_data stopwords
CMD streamlit run app.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'