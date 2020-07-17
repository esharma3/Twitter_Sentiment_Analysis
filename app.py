##########################################################################
#                   Importing dependencies here                          #
##########################################################################
import streamlit as st
from streamlit import caching

from PIL import Image
import PIL
import io
import requests
import sys

import tweepy
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotly.graph_objects as go


import nltk
# nltk.download("stopwords")
# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


from wordcloud import WordCloud, STOPWORDS
from textblob import TextBlob
import re
import time
import os


#########################################################################
#                    Validating the Credentials                         #
#########################################################################

consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

# creating the authentication object, setting access token and creating the api object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


#########################################################################
#                            Analysis                                   #
#########################################################################


def app():

    tweet_count = 0
    user_name = ""

    # st.sidebar.markdown(":slightly_smiling_face: :upside_down_face: :neutral_face: :expressionless: :smirk: :angry:")
    st.sidebar.header("Enter the Details Here!!")

    user_name = st.sidebar.text_area("Enter the Twitter Handle without @")

    tweet_count = st.sidebar.slider(
        "Select the number of Latest Tweets to Analyze",
        0, 50, 1
    )

    # st.sidebar.button("Click")
    st.markdown("Created By: [Ekta Sharma](https://www.linkedin.com/in/ektasharma3/)")  
    st.markdown("""# Twitter Sentiment Analyzer :slightly_smiling_face: :neutral_face: :angry: """)
    st.write("This app analyzes the Twitter tweets and returns the most commonly used words and the associated sentiments!! Note that Private account / Protected Tweets will not be accessible through this app.")
    st.write(":bird: Word Cloud and Sentiment Analysis Result will be based on the number of Latest Tweets selected on the Sidebar. :point_left:")

    # function to retrieve tweets 
    def get_tweets():

        tweets_list = []
        img_url = ""
        name = ""

        try:
            for tweet in api.user_timeline(
                id=user_name, count=tweet_count, tweet_mode="extended"
            ):  
                tweets_dict = {}
                tweets_dict["date_created"] = tweet.created_at
                tweets_dict["tweet_id"] = tweet.id
                tweets_dict["tweet"] = tweet.full_text

                tweets_list.append(tweets_dict)

            img_url = tweet.user.profile_image_url
            name = tweet.user.name
            screen_name = tweet.user.screen_name
            desc = tweet.user.description

        except BaseException as e:
            st.exception("Failed to retrieve the tweet."+str(e))
            sys.exit(1)


        return tweets_list, img_url, name, screen_name, desc 



    # function to prepare the data for word cloud and sentiment analysis
    extra_stopwords = ["The", "It", "it", "in", "In", "wh"]
    def prep_data(tweet):
        
        # cleaning the data    
        tweet = re.sub("https?:\/\/\S+", "", tweet) # replacing url with domain name
        tweet = re.sub("#[A-Za-z0–9]+", " ", tweet) # removing #mentions
        tweet = re.sub("#", " ", tweet) # removing hash tag 
        tweet = re.sub("\n", " ", tweet) # removing \n 
        tweet = re.sub("@[A-Za-z0–9]+", "", tweet) #Removing @mentions
        tweet = re.sub("RT", "", tweet) # removing RT
        tweet = re.sub("^[a-zA-Z]{1,2}$", "", tweet) # removing 1-2 char long words
        tweet = re.sub('\w*\d\w*', '', tweet) # removing words containing digits
        for word in extra_stopwords:
            tweet = tweet.replace(word, "")
        # lemmitizing
        lemmatizer = WordNetLemmatizer()
        new_s = ""
        for word in tweet.split(" "):
            lemmatizer.lemmatize(word)
            if word not in stopwords.words("english"):
                new_s += word + " "
                
        return new_s[:-1]


    # creating word cloud based on tweets data
    def wordcloud():

        # tweet_mask = np.array(Image.open('comment.png'))
        wordcloud_words = " ".join(tweet_df["clean_tweet"])
        wordcloud = WordCloud(
            height=2500,
            width=4000,
            # mask=tweet_mask,
            background_color="black",
            random_state=100,
            stopwords=STOPWORDS,
        ).generate(wordcloud_words)
        plt.figure(figsize=(15, 12), edgecolor="blue")
        plt.figure(edgecolor="blue")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig('cloud.jpg')
        img = Image.open("cloud.jpg") 
        return img


    # function to get the polarity score
    def getPolarity(tweet):
        sentiment_polarity = TextBlob(tweet).sentiment.polarity
        return sentiment_polarity

    # function to convert the polarity score into sentiment category    
    def getAnalysis(polarity_score):
        if polarity_score < 0:
            return "Negative"
        elif polarity_score == 0:
            return "Neutral"
        else:
            return "Positive"



    # function for plotting the sentiments
    def plot_sentiments():
        sentiment_df = pd.DataFrame(tweet_df["sentiment"].value_counts()).reset_index().rename(columns={"index": "sentiment_name"})
        fig = go.Figure([go.Bar(x=sentiment_df["sentiment_name"], y=sentiment_df["sentiment"])])
        fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, title="Sentiment Score"), plot_bgcolor="rgba(0,0,0,0)")
        return fig

    # main 
    # if (st.sidebar.button("Click To Analyze") and user_name != "" and tweet_count > 0) or (user_name != "" and tweet_count > 0):
    if user_name != "" and tweet_count > 0:

        with st.spinner("Please Wait!! Analysis is in Progress......:construction:"):
             time.sleep(5)
             # st.success("Finished!")

        tweets_list, img_url, name, screen_name, desc = get_tweets()

        # adding the retrieved tweet data into a dataframe
        tweet_df = pd.DataFrame([tweet for tweet in tweets_list])
        st.sidebar.info("Name: "+ name)
        st.sidebar.info("Screen Name: @"+ screen_name)
        st.sidebar.info("Description: "+ desc)

        # displaying the image on the sider bar
        response = requests.get(img_url)
        image_bytes = io.BytesIO(response.content)
        img = PIL.Image.open(image_bytes)
        st.sidebar.image(img)

        # calling the function to prep the data    
        tweet_df["clean_tweet"] = tweet_df["tweet"].apply(prep_data)
        # calling the function to create the word cloud
        img=wordcloud()
        st.success("Word Cloud for Twitter Handle @"+user_name+" based on the last "+str(tweet_count)+" tweet(s)!!")
        st.image(img)
        # calling the function to create sentiment scoring
        tweet_df["polarity"] = tweet_df["clean_tweet"].apply(getPolarity)
        tweet_df["sentiment"] = tweet_df["polarity"].apply(getAnalysis)
        # calling the function for plotting the sentiments
        senti_fig=plot_sentiments()
        st.success("Sentiment Analysis for Twitter Handle @"+user_name+" based on the last "+str(tweet_count)+" tweet(s)!!")
        st.plotly_chart(senti_fig, use_container_width=True)


        # displaying latest tweets
        st.subheader("Latest Tweets (Max 10 returned if more than 10 selected using the sidebar)!!")
        st.success("Latest Tweets from the Twitter Handle @"+user_name)

        length = 10 if len(tweet_df) > 10 else len(tweet_df)

        for i in range(length):
            st.write("Tweet Number: "+str(i+1)+", Tweet Date: "+str(tweet_df["date_created"][i]))
            st.info(tweet_df["tweet"][i])
    else:
        st.info(":point_left: Enter the Twitter Handle & Number of Tweets to Analyze on the SideBar :point_left:")



##############################################################################################
#                                      Main                                                  #
############################################################################################## 


if __name__ == "__main__":

    # caching.clear_cache()
    # st.empty()
    app()


