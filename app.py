import os
import re
import pickle
from datetime import datetime
import streamlit as st
import tensorflow as tf

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
# SESSION STATE INIT
# ==========================================

if "sms_input" not in st.session_state:
    st.session_state.sms_input = ""
if "history" not in st.session_state:
    st.session_state.history = []

SAMPLE_MESSAGES = {
    "🚨 Phishing": "URGENT! Your bank KYC is suspended. Click http://bit.ly/verify-now to update PAN within 24 hrs or account will be blocked.",
    "🎁 Prize Scam": "CONGRATULATIONS! You have won ₹50,000 cash reward! Call 9876543210 now to claim your free prize today.",
    "✅ Legitimate": "Hey, are we still on for dinner at 8 PM? Let me know if I should pick up anything on the way.",
}

def set_sample(text: str):
    st.session_state.sms_input = text

def clear_input():
    st.session_state.sms_input = ""

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
    max-width: 1080px;
    padding-top: 2rem;
    padding-bottom: 2.5rem;
}

/* Hero */
.hero {
    background: linear-gradient(125deg, #241b54 0%, #5846cc 60%, #7b68ee 100%);
    padding: 38px 36px;
    border-radius: 22px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 12px 32px rgba(75, 60, 160, 0.18);
}

.hero h1 {
    font-size: 36px;
    font-weight: 800;
    margin: 0 0 10px 0;
    color: white;
    letter-spacing: -0.5px;
}

.hero p {
    font-size: 15px;
    color: #e6e2ff;
    margin: 0;
    line-height: 1.65;
    max-width: 680px;
}

.hero-tag {
    display: inline-block;
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-bottom: 14px;
}

/* Section Headers */
.section-title {
    font-size: 20px;
    font-weight: 750;
    color: #241f46;
    margin-bottom: 6px;
}

.section-subtitle {
    color: #6f6b85;
    font-size: 13.5px;
    margin-bottom: 16px;
}

/* Text Area */
.stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #ddd8f6 !important;
    border-radius: 14px !important;
    color: #262247 !important;
    font-size: 15px !important;
    padding: 15px !important;
    line-height: 1.55 !important;
}

.stTextArea textarea:focus {
    border-color: #6b58e2 !important;
    box-shadow: 0 0 0 3px rgba(107, 88, 226, 0.14) !important;
}

/* Primary Button */
.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #5e4cd4, #826ff0);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 700;
    font-size: 15px;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"]:hover {
    background: #4d3cb8;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(94, 76, 212, 0.25);
}

/* Secondary Buttons (Samples / Clear) */
.stButton > button[kind="secondary"] {
    background: white;
    color: #3d356b;
    border: 1px solid #dfdcf5;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
    transition: all 0.15s ease;
}

.stButton > button[kind="secondary"]:hover {
    border-color: #7663e9;
    color: #5e4cd4;
    background: #faf9ff;
}

/* Result Cards */
.result-card {
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    margin-top: 12px;
}

.spam-card {
    background: #fff1f2;
    border: 1.5px solid #fecdd3;
    color: #be123c;
}

.ham-card {
    background: #ecfdf5;
    border: 1.5px solid #a7f3d0;
    color: #047857;
}

.result-card h2 {
    font-size: 24px;
    font-weight: 800;
    margin: 8px 0 4px 0;
}

.result-number {
    font-size: 40px;
    font-weight: 800;
    margin: 10px 0;
    letter-spacing: -1px;
}

.risk-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* Custom Meter */
.meter-track {
    width: 100%;
    height: 10px;
    background: #e9e6f8;
    border-radius: 999px;
    overflow: hidden;
    margin: 14px 0 6px 0;
}

.meter-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* Signal Badges */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}

.signal-badge {
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

.safe-badge {
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

/* Info Card */
.info-card {
    background: white;
    padding: 22px;
    border: 1px solid #e9e5fa;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(41, 32, 92, 0.04);
}

.info-step {
    margin-bottom: 16px;
}

.info-step:last-child {
    margin-bottom: 0;
}

.info-card h4 {
    color: #2f2857;
    font-size: 14.5px;
    font-weight: 700;
    margin: 0 0 4px 0;
}

.info-card p {
    color: #706c86;
    font-size: 13px;
    line-height: 1.55;
    margin: 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #8a869f;
    font-size: 12.5px;
    padding: 28px 10px 10px 10px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD MODEL & TOKENIZER
# ==========================================

MODEL_PATH = "sms_spam_gru.keras"
TOKENIZER_PATH = "sms_tokenizer.pkl"
MAX_LEN = 100

@st.cache_resource
def load_assets():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TOKENIZER_PATH):
        raise FileNotFoundError(
            f"Missing '{MODEL_PATH}' or '{TOKENIZER_PATH}' in the app directory."
        )
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, "rb") as file:
        tok = pickle.load(file)
    return model, tok

try:
    gru_model, tokenizer = load_assets()
except Exception as e:
    st.error(f"Could not load model or tokenizer: {e}")
    st.stop()


# ==========================================
# NLP & HEURISTIC HELPERS
# ==========================================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def detect_signals(raw_text: str) -> list[str]:
    signals = []
    if re.search(r"(http\S+|www\S+|\bbit\.ly\b|\btinyurl\b)", raw_text, re.I):
        signals.append("🔗 Contains URL / short link")
    if re.search(r"(₹|\$|£|€|\brs\.?\s*\d|\binr\b|\bfree\b|\bwon\b|\bprize\b|\bcash\b)", raw_text, re.I):
        signals.append("💰 Money / reward terms")
    if re.search(r"(\burgent\b|\bimmediately\b|\b24\s*hrs?\b|\bblocked\b|\bsuspended\b|\bverify\b|\bkyc\b)", raw_text, re.I):
        signals.append("⏳ Urgency / account threat")
    if re.search(r"\b\d{10}\b", raw_text):
        signals.append("📞 Phone number detected")
    if sum(1 for c in raw_text if c.isupper()) > max(8, len(raw_text) * 0.35):
        signals.append("🔠 Excessive CAPS")
    return signals

def predict_sms(message: str, threshold: float = 0.5):
    cleaned = clean_text(message)
    sequence = tokenizer.texts_to_sequences([cleaned])
    token_count = len(sequence[0])

    padded = tf.keras.utils.pad_sequences(
        sequence,
        maxlen=MAX_LEN,
        padding="post",
        truncating="post"
    )

    probability = float(gru_model.predict(padded, verbose=0)[0][0])
    prediction = "SPAM" if probability >= threshold else "HAM"
    return prediction, probability, cleaned, token_count


# ==========================================
# SIDEBAR SETTINGS
# ==========================================

with st.sidebar:
    st.header("⚙️ Model Settings")
    threshold = st.slider(
        "Spam Sensitivity Threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.50,
        step=0.05,
        help="Lower values catch more spam (higher sensitivity); higher values reduce false alarms."
    )
    st.caption(f"Messages with spam probability ≥ **{threshold:.0%}** are flagged as SPAM.")
    if st.session_state.history:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# ==========================================
# HERO SECTION
# ==========================================

st.markdown("""
<div class="hero">
    <div class="hero-tag">🛡️ DEEP LEARNING SMS SECURITY</div>
    <h1>SpamShield</h1>
    <p>
        Real-time SMS spam detection powered by a GRU neural network.
        Paste any message below—or try a sample—to inspect its spam probability and risk signals.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# MAIN INPUT SECTION
# ==========================================

left, right = st.columns([1.75, 1], gap="large")

with left:
    st.markdown('<div class="section-title">📩 Analyze Your Message</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Try a quick sample or paste your own SMS below.</div>', unsafe_allow_html=True)

    # Sample buttons
    sample_cols = st.columns(len(SAMPLE_MESSAGES))
    for col, (label, sample_text) in zip(sample_cols, SAMPLE_MESSAGES.items()):
        col.button(label, on_click=set_sample, args=(sample_text,), use_container_width=True)

    message = st.text_area(
        "SMS Message",
        key="sms_input",
        placeholder="Example: Congratulations! You have won a free prize. Click here...",
        height=165,
        label_visibility="collapsed"
    )

    # Action row
    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        check_button = st.button("🔍 Analyze Message", type="primary", use_container_width=True)
    with btn_col2:
        st.button("Clear", on_click=clear_input, use_container_width=True)

with right:
    st.markdown('<div class="section-title">✨ How It Works</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <div class="info-step">
            <h4>01 · Text Preprocessing</h4>
            <p>Normalizes casing, strips URLs/punctuation, and tokenizes up to 100 tokens.</p>
        </div>
        <div class="info-step">
            <h4>02 · GRU Inference</h4>
            <p>A Gated Recurrent Unit (GRU) evaluates word sequences and context.</p>
        </div>
        <div class="info-step">
            <h4>03 · Risk & Signal Breakdown</h4>
            <p>Combines model probability with common phishing indicators for clarity.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# DISPLAY PREDICTION
# ==========================================

if check_button:
    if not message.strip():
        st.warning("Please enter a message before analyzing.")
    else:
        with st.spinner("Analyzing SMS..."):
            prediction, prob, cleaned, token_count = predict_sms(message, threshold)
            signals = detect_signals(message)

        # Save to session history
        st.session_state.history.insert(0, {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Result": prediction,
            "Spam Score": f"{prob * 100:.1f}%",
            "Message": message[:80] + ("..." if len(message) > 80 else "")
        })

        st.markdown("---")
        st.markdown('<div class="section-title">📊 Analysis Result</div>', unsafe_allow_html=True)

        if not cleaned:
            st.info("Note: After removing URLs and symbols, no text tokens remained for the GRU model. Rely on the signal badges below.")

        res_col, detail_col = st.columns([1.2, 1], gap="large")

        with res_col:
            if prediction == "SPAM":
                risk_label = "HIGH RISK" if prob >= 0.8 else "MODERATE RISK"
                bar_color = "#e11d48" if prob >= 0.8 else "#f59e0b"
                st.markdown(f"""
                <div class="result-card spam-card">
                    <span class="risk-pill" style="background:#ffe4e6; color:#be123c;">{risk_label}</span>
                    <div style="font-size:38px;">🚨</div>
                    <h2>SPAM DETECTED</h2>
                    <div class="result-number">{prob * 100:.2f}%</div>
                    <p style="font-size:13.5px; margin:0;">Predicted spam probability (threshold: {threshold:.0%})</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                safe_conf = (1 - prob) * 100
                bar_color = "#10b981"
                st.markdown(f"""
                <div class="result-card ham-card">
                    <span class="risk-pill" style="background:#d1fae5; color:#047857;">LOW RISK</span>
                    <div style="font-size:38px;">✅</div>
                    <h2>LEGITIMATE MESSAGE (HAM)</h2>
                    <div class="result-number">{safe_conf:.2f}%</div>
                    <p style="font-size:13.5px; margin:0;">Confidence that this message is safe (Spam score: {prob * 100:.2f}%)</p>
                </div>
                """, unsafe_allow_html=True)

            # Custom color-coded spam probability bar
            st.markdown(f"""
            <div class="meter-track">
                <div class="meter-fill" style="width: {min(max(prob * 100, 2), 100):.1f}%; background: {bar_color};"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12px; color:#77748d;">
                <span>0% (Safe)</span>
                <span>Spam Score: {prob * 100:.1f}%</span>
                <span>100% (Spam)</span>
            </div>
            """, unsafe_allow_html=True)

        with detail_col:
            st.markdown("#### 🔎 Detected Signals")
            if signals:
                badges_html = "".join(f'<span class="signal-badge">{s}</span>' for s in signals)
                st.markdown(f'<div class="badge-row">{badges_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="badge-row"><span class="safe-badge">✓ No obvious phishing patterns found</span></div>',
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🧠 What the GRU model saw"):
                st.write(f"**Known vocabulary tokens:** `{token_count}` / `{MAX_LEN}`")
                st.code(cleaned if cleaned else "(empty after cleaning)", language="text")

        st.caption(
            "Spam score reflects the GRU model's predicted probability, not a guarantee. "
            "Never share OTPs or click unknown links."
        )


# ==========================================
# RECENT HISTORY
# ==========================================

if st.session_state.history:
    st.markdown("---")
    with st.expander(f"🕒 Recent Checks ({len(st.session_state.history)})", expanded=False):
        st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)


# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    Built with Python · TensorFlow · GRU · Streamlit<br>
    <strong>SpamShield</strong> | Deep Learning NLP Project
</div>
""", unsafe_allow_html=True)
