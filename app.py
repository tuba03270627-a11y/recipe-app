import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus
import time

# --- アプリの基本設定 ---
st.set_page_config(page_title="AI Chef's Special Menu", page_icon="📜", layout="centered")

# --- デザイン（CSS） ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500&family=Playfair+Display:ital,wght@1,700&display=swap');

    /* ★★★ ここからが背景の修正箇所 ★★★ */
    .stApp {
        background-color: #f5f0e1 !important;
        background-image: url("https://www.transparenttextures.com/patterns/old-paper.png") !important;
        background-attachment: fixed !important;
        background-size: cover !important;
    }
    /* ★★★ ここまでが背景の修正箇所 ★★★ */

    /* すべての文字の基本色を、読みやすい濃い色に固定 */
    body, p, h1, h2, h3, h4, h5, h6, label, summary, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: #4a4a4a !important;
        font-family: 'Noto Serif JP', serif;
    }
    /* タイトルなど、一部の色だけアクセントとして変更 */
    h1, h2, a {
        color: #a88f59 !important;
        font-family: 'Playfair Display', serif !important;
    }
    a { font-weight: bold; }

    /* --- メインコンテンツのコンテナ（メニュー用紙）--- */
    .main .block-container {
        max-width: 700px; padding: 3rem; background-color: #fffef8;
        border: 1px solid #d4c8b8; border-radius: 5px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        position: relative;
    }
    .main .block-container::before {
        content: ''; position: absolute; top: 15px; left: 15px; right: 15px; bottom: 15px;
        border: 2px double #d8c9b1; border-radius: 3px; pointer-events: none;
    }
    
    h1 { font-style: italic; text-align: center; padding-bottom: 0.3em; margin-bottom: 1em; font-size: 3.2em; letter-spacing: 1px; }
    .st-emotion-cache-1yycg8b p { text-align: center; font-size: 1em; }
    h2 { font-style: italic; text-align: center; margin-top: 2em; margin-bottom: 1.5em; font-size: 2.2em; }
    h3 { border-bottom: 1px dotted #b8b0a0; padding-bottom: 0.5em; margin-top: 1.5em; margin-bottom: 1em; font-size: 1.3em; }
    
    /* --- 入力欄 --- */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #c9c3b3 !important; background-color: #fff !important; border-radius: 3px;
        padding: 10px !important; font-size: 16px; color: #4a4a4a !important;
    }
    
    /* --- ボタン --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #a88f59 !important; color: white !important; border: 1px solid #a88f59 !important;
        border-radius: 5px !important; font-family: 'Noto Serif JP', serif !important; font-weight: 500 !important;
        letter-spacing: 1px !important; padding: 12px 24px !important; font-size: 18px !important;
        transition: background-color 0.3s ease !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #8c7749 !important; border-color: #8c7749 !important; color: white !important;
    }
    
    /* --- 結果表示（Expander） --- */
    details { border: 1px solid #e0d8c0; border-radius: 5px; padding: 1em; margin-bottom: 1em; background-color: rgba(255,255,255,0.3); }
    details summary { font-weight: 700; font-size: 1.1em; cursor: pointer; color: #4a4a4a !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- APIキーの設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.sidebar.info("アプリをデプロイする際は、StreamlitのSecrets機能でAPIキーを設定すると、この欄は表示されなくなります。")
    api_key = st.sidebar.text_input("ここにGoogle AI StudioのAPIキーを貼り付けてください:", type="password", key="api_key_input")

if api_key:
    genai.configure(api_key=api_key)

# --- 関数定義 ---
def generate_full_menu(ingredients, request_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    あなたは格式高いレストランのシェフです。以下の【使用する食材】を創造的に活かし、【お客様からのご要望】に沿った献立を考えてください。
    ご要望に品数の指定がない場合は、主菜1品と副菜1品を基本としてください。
    回答は、必ず以下の
