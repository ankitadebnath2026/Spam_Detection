
import streamlit as st
import tensorflow as tf
import pickle
import re
import numpy as np

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="SMS Spam Detector",
    page_icon="📩",
    layout="centered"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
.main {
    background-color: #f8f9fc;
}
.title {
    text-align: center;
    color: #5b4bdb;
    font-size: 38px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #777;
    font-size: 16px;
}
.result-box {
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-top: 20px;
}
.spam {
    background-color: #ffe5e5;
    color: #d62828;
}
.ham {
    background-color: #e3fcef;
    color: #16834a;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Model and Tokenizer
# -------------------------------
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("sms_spam_gru.keras")

@st.cache_resource
def load_tokenizer():
    with open("sms_tokenizer.pkl", "rb") as file:
        return pickle.load(file)

gru_model = load_model()
tokenizer = load_tokenizer()

# -------------------------------
# Constants
# -------------------------------
MAX_LEN = 100

# -------------------------------
# Text Cleaning
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------
# Prediction Function
# -------------------------------
def predict_sms(message):

    cleaned_message = clean_text(message)

    sequence = tokenizer.texts_to_sequences(
        [cleaned_message]
    )

    padded = tf.keras.utils.pad_sequences(
        sequence,
        maxlen=MAX_LEN,
        padding="post",
        truncating="post"
    )

    probability = float(
        gru_model.predict(padded, verbose=0)[0][0]
    )

    prediction = "SPAM" if probability >= 0.5 else "HAM"

    return prediction, probability

# -------------------------------
# Main UI
# -------------------------------
st.markdown(
    '<div class="title">📩 SMS Spam Detector</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered SMS classification using GRU</div>',
    unsafe_allow_html=True
)

st.write("")

message = st.text_area(
    "Enter your SMS message:",
    placeholder="Example: Congratulations! You won a free prize...",
    height=150
)

if st.button("🔍 Check Message", use_container_width=True):

    if not message.strip():
        st.warning("Please enter an SMS message.")

    else:
        prediction, probability = predict_sms(message)

        st.markdown("---")

        if prediction == "SPAM":
            st.markdown(
                f"""
                <div class="result-box spam">
                    <h2>🚨 SPAM MESSAGE</h2>
                    <h3>Spam Probability: {probability * 100:.2f}%</h3>
                    <p>Be careful! This message may be suspicious.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                f"""
                <div class="result-box ham">
                    <h2>✅ HAM MESSAGE</h2>
                    <h3>Spam Probability: {probability * 100:.2f}%</h3>
                    <p>This message is classified as normal.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.caption("Built with Python, TensorFlow, GRU and Streamlit.")
