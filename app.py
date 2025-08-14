import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの特別献立", page_icon="📜", layout="centered") # レイアウトを中央寄せに変更

# --- デザイン（CSS） ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=Playfair+Display:ital,wght@1,700&display=swap');

    /* --- 背景 --- */
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/old-paper.png");
        background-attachment: fixed;
        background-size: cover;
    }

    /* --- 全体のフォントと文字色 --- */
    body, .st-emotion-cache-1qg05j3, .st-emotion-cache-1yycg8b p {
        font-family: 'Cormorant Garamond', serif;
        color: #5a483a; /* セピアブラウン */
        font-size: 18px;
    }

    /* --- メインコンテンツのコンテナ（メニュー用紙）--- */
    .main .block-container {
        max-width: 800px;
        padding: 2rem;
        background-color: rgba(253, 251, 243, 0.9); /* 少しクリーム色がかった半透明の白 */
        border: 1px solid #d4c8b8;
        border-radius: 2px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* --- タイトル --- */
    h1 {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #8c7853; /* アンティークゴールド */
        text-align: center;
        border-bottom: 2px double #d4c8b8;
        padding-bottom: 0.5em;
        margin-bottom: 1.5em;
        font-size: 3em;
    }

    /* --- 入力欄 --- */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #d4c8b8 !important;
        background-color: #fff;
    }

    /* --- ボタン --- */
    .stButton>button {
        background-color: #8c7853;
        color: white;
        border: 1px solid #8c7853;
        border-radius: 2px;
        font-family: 'Cormorant Garamond', serif;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #7a6843;
        border-color: #7a6843;
    }
    
    /* --- 結果表示 --- */
    h2 {
        text-align: center;
        color: #8c7853;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        margin-top: 2em;
        font-size: 2.2em;
    }
    h3 {
        color: #5a483a;
        font-weight: bold;
        border: none;
        text-align: center;
        margin-top: 1.5em;
        letter-spacing: 0.5px;
    }
    a {
        color: #8c7853 !important;
        font-weight: bold;
    }
    .st-emotion-cache-1r6slb0 {
        background-color: transparent;
        border: none;
        padding: 0 !important;
    }
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
def create_search_link(dish_name):
    query = f"{dish_name} レシピ"
    return f"https://www.google.com/search?q={quote_plus(query)}"

def generate_menu(ingredients, request_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    あなたは格式高いレストランのシェフです。以下の【使用する食材】を創造的に活かし、【お客様からのご要望】に沿った、気品のある献立（主菜1品、副菜1品）を考えてください。
    回答は、必ず以下のJSONフォーマットで、料理名のみを返してください。説明や挨拶は絶対に含めないでください。
    {{
      "main_dish": "主菜の料理名",
      "side_dish": "副菜の料理名"
    }}
    ---
    【お客様からのご要望】
    {request_text if request_text else "シェフのおまかせ"}

    【使用する食材】
    {ingredients}
    """
    response = model.generate_content(prompt)
    cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

# --- Streamlitの画面表示 ---
st.title('AI Chef\'s Special Menu')
st.write("お客様の食材とご要望を元に、AIシェフが特別な献立をご提案いたします。")

# --- UI（入力部分） ---
ingredients = st.text_area('ご使用になる食材をお聞かせください', placeholder='例: 鶏もも肉、パプリカ、玉ねぎ、白ワイン')
user_request = st.text_input('その他、ご要望はございますか？（任意）', placeholder='例: 洋風で、ワインに合う軽めのもの')

# --- 検索実行と結果表示 ---
if st.button('献立を提案いただく', use_container_width=True):
    if not api_key:
        st.error("恐れ入りますが、先にAPIキーの設定をお願いいたします。")
    elif not ingredients:
        st.info('まずは、ご使用になる食材をお聞かせください。')
    else:
        with st.spinner('シェフが特別な献立を考案しております... 📜'):
            try:
                menu = generate_menu(ingredients, user_request)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

                st.header("本日の一皿")
                
                if main_dish_name:
                    st.subheader(f"{main_dish_name}")
                    st.markdown(f"▷ *作り方を調べる*({create_search_link(main_dish_name)})")
                
                st.markdown("---")

                if side_dish_name:
                    st.subheader(f"{side_dish_name}")
                    st.markdown(f"▷ *作り方を調べる*({create_search_link(side_dish_name)})")

            except Exception as e:
                st.error(f"申し訳ございません、エラーが発生いたしました: {e}")
                st.error("AIシェフが応答できませんでした。少し時間をおいてから、再度お試しください。")
