import requests
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from transformers import AutoTokenizer, AutoModelForCausalLM
import streamlit as st
import transformers
print(transformers.__version__)


# Load the LLaMA model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-13b-chat")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-13b-chat", device_map="auto")

def answer_question(question, context):
    # Format the prompt as a conversational input for better results with LLaMA
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    outputs = model.generate(inputs['input_ids'], max_length=150)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Process the model output to get the answer part only
    return answer.split("Answer:")[-1].strip()

st.title("Financial Chatbot")
context = st.text_area("Enter the context:")
question = st.text_input("Ask a question:")

if st.button("Get Answer"):
    if context and question:
        answer = answer_question(question, context)
        st.write("Answer:", answer)
    else:
        st.write("Please provide both context and a question.")

# Define functions (same as before)
def get_yahoo_finance_articles(base_url, count=26):
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', class_='js-stream-content')
        result = [{"title": article.find('h3').get_text(strip=True), "link": article.find('a')['href']} for article in articles[:count]]
        return result
    else:
        return None

def get_links(articles):
    return [
        article['link'] if article['link'].startswith('http') else f"https://finance.yahoo.com{article['link']}"
        for article in articles
    ]

def get_paragraphs_text(soup):
    paragraphs = soup.find_all('p')
    return [paragraph.text.lower() for paragraph in paragraphs]

def extract_text_from_article(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = get_paragraphs_text(soup)
    return text

def parse_all_articles(links):
    return ['.'.join(extract_text_from_article(link)) for link in links]

def data_preprocessing(bdd):
    preprocessed_bdd = []
    lemmatizer = WordNetLemmatizer()
    for doc in bdd:
        tokens = sent_tokenize(doc)
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        preprocessed_bdd.append(' '.join(lemmatized_tokens))
    return preprocessed_bdd

def get_best_article(user_input):
    preprocessed_bdd.append(user_input)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(preprocessed_bdd)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    most_similar_index = np.argmax(cosine_sim)
    if cosine_sim[0][most_similar_index] < 1 and cosine_sim[0][most_similar_index] > 0.1:
        return preprocessed_bdd[most_similar_index]
    else:
        return "I am sorry, I could not understand you."

def generate_answer_bert(question, context):
    inputs = tokenizer(question, context, return_tensors='pt', max_length=512, truncation=True)
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
    cleaned_answer = answer.replace("[CLS]", "").replace("[SEP]", "").strip()
    return cleaned_answer

def get_final_answer(question, bdd):
    best_context = get_best_context(question, bdd)
    bert_answer = generate_answer_bert(question, best_context)
    return bert_answer

def get_best_context(question, articles):
    articles.append(question)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(articles)
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    best_index = similarities.argmax()
    articles.pop()
    return articles[best_index]

def load_articles():
    articles = get_yahoo_finance_articles("https://finance.yahoo.com/topic/personal-finance-news/") + \
               get_yahoo_finance_articles("https://finance.yahoo.com/") + \
               get_yahoo_finance_articles("https://finance.yahoo.com/calendar/") + \
               get_yahoo_finance_articles("https://finance.yahoo.com/topic/stock-market-news/")
    urls = get_links(articles)
    bdd = parse_all_articles(urls)
    preprocessed_bdd = data_preprocessing(bdd)
    return preprocessed_bdd

# Load articles on app start
preprocessed_bdd = load_articles()
