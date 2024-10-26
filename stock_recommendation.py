import pandas as pd
import streamlit as st
import re  # Importing the regular expressions module
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to get item recommendations based on user input (date and ticker)
def get_recommendations(date, ticker):
    # Find the index of the first row where the user input date matches in the column Date
    filtered_df = df[(df['date'] == date) & (df['ticker'] == ticker)]
 
    if not filtered_df.empty:
        index = filtered_df.index[0]
        
        # Calculate the similarity between items represented by their TF-IDF vectors
        similarities = cosine_similarity(tfidf_matrix, tfidf_matrix)
        cosine_scores = similarities[index]
        st.write(cosine_scores)
        # Get the 3 indices of items with the highest similarity scores
        indices = cosine_scores.argsort()[:-4:-1]
        # Return recommended items
        recommendations = df['date'].iloc[indices].tolist()
        return recommendations
    else:
        st.write(f"No data found for date {date} and ticker {ticker}")

# Function to display the details on each recommended date
def display_recommended_dates(recommendations, ticker):
    if recommendations is not None:
        for i in recommendations:
            st.write(df[(df['date'] == f"{i}") & (df['ticker'] == ticker)])
    else:
        st.write(f"No data found for recommendations {recommendations}")

# Example usage
def get_stock_recommendation(): 
    global df
    df = pd.read_csv("./Data/ticker_history.csv", delimiter=';')
    df['Features'] = df[['open', 'high', 'low', 'close', 'ticker']].astype(str).agg(' '.join, axis=1)
    vectorizer = TfidfVectorizer(stop_words='english')
    global tfidf_matrix
    tfidf_matrix = vectorizer.fit_transform(df['Features'])

    st.write("Chatbot: Welcome to the stock recommendation module!")

    # Date input with validation
    date_input = st.text_input("Chatbot: Please enter a date (MM/DD/YYYY):", key="date_input")
    if date_input and not re.match(r"^\d{2}/\d{2}/\d{4}$", date_input):
        st.warning("Please enter a valid date format (MM/DD/YYYY).")
        return  # Early return to avoid further processing

    # Ticker input with dropdown
    ticker_options = df['ticker'].unique().tolist()
    ticker = st.selectbox("Chatbot: Please select a ticker", ticker_options)

    if date_input:  # Proceed only if a valid date has been entered
        recommendations = get_recommendations(date_input, ticker)
        if recommendations:
            st.write(f"\nUser print Date and Ticker: {date_input}, {ticker}")
            st.write(f"\nRecommended Dates: {recommendations}")
            display_recommended_dates(recommendations, ticker)
        else:
            st.write(f"No recommendations found for date {date_input} and ticker {ticker}.")

# Uncomment the following line to run the function when executing the script
st.title("Stock Recommendation")
st.write("Welcome to the Stock Recommendation page!")
st.write("This page consist of having giving you dates of a company where the features are really near ")

st.write("To test this you can set the date to 08/12/2023 with aapl as the ticker\n")
st.write("--------------------------------------------------------")

get_stock_recommendation()
