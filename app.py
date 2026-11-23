
import streamlit as st
import tensorflow as tf
import pickle
import re

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SpamShield | SMS Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f6f5ff;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Header */

.hero {
    background: linear-gradient(120deg, #29205c, #6553d9);
    padding: 42px 35px;
    border-radius: 22px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(75, 60, 160, 0.16);
}

.hero h1 {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 10px;
    color: white;
}

.hero p {
    font-size: 15px;
    color: #e4dfff;
    margin-bottom: 0;
    line-height: 1.7;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 12px;
    margin-bottom: 16px;
}

/* Section */

.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #28234c;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #77748d;
    font-size: 13px;
    margin-bottom: 18px;
}

/* Input */

.stTextArea textarea {
    background: white !important;
    border: 1.5px solid #dedaf5 !important;
    border-radius: 14px !important;
    color: #29254a !important;
    font-size: 15px !important;
    padding: 15px !important;
}

.stTextArea textarea:focus {
    border-color: #7663e9 !important;
    box-shadow: 0 0 0 2px rgba(118,99,233,0.12) !important;
}

/* Button */

.stButton > button {
    background: linear-gradient(100deg, #6553d9, #8875f0);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 13px 20px;
    font-weight: 700;
    font-size: 15px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #5140bd;
    color: white;
    border: none;
    transform: translateY(-2px);
}

/* Result */

.result-card {
    padding: 27px;
    border-radius: 18px;
    text-align: center;
    margin-top: 20px;
}

.spam-card {
    background: #fff0f0;
    border: 1px solid #ffcaca;
    color: #c52c42;
}

.ham-card {
    background: #eafff3;
    border: 1px solid #b9efd0;
    color: #16834a;
}

.result-card h2 {
    font-size: 27px;
    font-weight: 800;
    margin-bottom: 8px;
}

.result-card p {
    font-size: 14px;
    margin-bottom: 0;
}

.result-number {
    font-size: 38px;
    font-weight: 800;
    margin: 12px 0;
}

/* Info cards */

.info-card {
    background: white;
    padding: 20px;
    border: 1px solid #e9e5fa;
    border-radius: 16px;
    height: 100%;
}

.info-card h4 {
    color: #38305f;
    font-size: 15px;
    margin-bottom: 8px;
}

.info-card p {
    color: #77748d;
    font-size: 13px;
    line-height: 1.6;
}

/* Footer */

.footer {
    text-align: center;
    color: #89859e;
    font-size: 12px;
    padding: 22px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD MODEL AND TOKENIZER
# ==========================================

@st.cache_resource
def load_model():
    return tf.keras.models.load_model("sms_spam_gru.keras")

@st.cache_resource
def load_tokenizer():
    with open("sms_tokenizer.pkl", "rb") as file:
        return pickle.load(file)

try:
    gru_model = load_model()
    tokenizer = load_tokenizer()
except Exception as e:
    st.error(f"Could not load model or tokenizer: {e}")
    st.stop()


# ==========================================
# CONSTANTS
# ==========================================

MAX_LEN = 100


# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ==========================================
# PREDICTION
# ==========================================

def predict_sms(message):

    cleaned_message = clean_text(message)

    sequence = tokenizer.texts_to_sequences([cleaned_message])

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


# ==========================================
# HERO SECTION
# ==========================================

st.markdown("""
<div class="hero">
    <div class="hero-tag">🛡️ AI POWERED SECURITY</div>
    <h1>SpamShield</h1>
    <p>
        Intelligent SMS Spam Detection powered by Deep Learning.
        Analyze your messages and identify suspicious content
        using a GRU neural network.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# MAIN INPUT SECTION
# ==========================================

left, right = st.columns([1.7, 1], gap="large")

with left:

    st.markdown(
        '<div class="section-title">📩 Analyze Your Message</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Paste your SMS below to check whether it is spam or legitimate.</div>',
        unsafe_allow_html=True
    )

    message = st.text_area(
        "SMS Message",
        placeholder="Example: Congratulations! You have won a free prize. Click here...",
        height=180,
        label_visibility="collapsed"
    )

    check_button = st.button(
        "🔍  Analyze Message",
        use_container_width=True
    )

with right:

    st.markdown(
        '<div class="section-title">✨ How it works</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <h4>01 · Enter Message</h4>
        <p>Paste the SMS you want to analyze.</p>
        <h4>02 · AI Analysis</h4>
        <p>Our trained GRU model processes the text.</p>
        <h4>03 · Get Result</h4>
        <p>View the Spam or Ham prediction and spam score.</p>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# DISPLAY PREDICTION
# ==========================================

if check_button:

    if not message.strip():
        st.warning("Please enter a message before analyzing.")

    else:

        with st.spinner("Analyzing your SMS..."):

            prediction, probability = predict_sms(message)

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📊 Analysis Result</div>',
            unsafe_allow_html=True
        )

        if prediction == "SPAM":

            st.markdown(f"""
            <div class="result-card spam-card">
                <div style="font-size:42px;">🚨</div>
                <h2>SPAM MESSAGE DETECTED</h2>
                <div class="result-number">{probability * 100:.2f}%</div>
                <p>Spam score · The model classified this message as suspicious.</p>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown(f"""
            <div class="result-card ham-card">
                <div style="font-size:42px;">✅</div>
                <h2>NORMAL MESSAGE (HAM)</h2>
                <div class="result-number">{probability * 100:.2f}%</div>
                <p>Spam score · The model classified this message as normal.</p>
            </div>
            """, unsafe_allow_html=True)

        st.progress(probability)

        st.caption(
            "Spam score represents the model's predicted probability, "
            "not a guarantee that the message is safe or fraudulent."
        )


# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    Built with ❤️ using Python · TensorFlow · GRU · Streamlit
    <br><br>
    SpamShield | Deep Learning NLP Project
</div>
""", unsafe_allow_html=True)
