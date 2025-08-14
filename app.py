import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの特別献立", page_icon="📜", layout="centered")

# --- デザイン（CSS） ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=Playfair+Display:ital,wght@1,700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400&display=swap');

    /* --- 背景 --- */
    .stApp {
        background-color: #f5f0e1; /* 薄いベージュ */
    }

    /* --- メインコンテンツのコンテナ（メニュー用紙）--- */
    .main .block-container {
        max-width: 700px;
        padding: 3rem;
        background-color: #fffef8; /* ほぼ白 */
        border: 1px solid #e0d8c0;
        border-radius: 5px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        position: relative; /* 枠線の基準点 */
    }

    /* --- メニュー用紙の装飾的な枠線（CSSだけで実現）--- */
    .main .block-container::before,
    .main .block-container::after {
        content: '';
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        bottom: 10px;
        border: 1px solid #d8c9b1;
        border-radius: 3px;
        pointer-events: none;
    }
    .main .block-container::before {
        top: 20px;
        left: 20px;
        right: 20px;
        bottom: 20px;
        border: 1px solid #e5dfd1;
        border-radius: 1px;
    }

    /* --- 全体のフォントと文字色 --- */
    body, .st-emotion-cache-1qg05j3, .st-emotion-cache-1yycg8b p {
        font-family: 'Noto Serif JP', serif; /* 和風にも合う上品なセリフ体 */
        color: #3d3d3d;
        font-size: 17px;
        line-height: 1.7;
    }

    /* --- タイトル --- */
    h1 {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #a88f59; /* ゴールドブラウン */
        text-align: center;
        padding-bottom: 0.3em;
        margin-bottom: 1em;
        font-size: 3.5em;
        letter-spacing: 1px;
    }

    /* --- サブタイトル --- */
    h2 {
        text-align: center;
        color: #a88f59;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        margin-top: 2em;
        margin-bottom: 1em;
        font-size: 2.5em;
    }

    /* --- 料理名 --- */
    h3 {
        color: #3d3d3d;
        font-weight: bold;
        border-bottom: 1px dotted #b8b0a0;
        padding-bottom: 0.3em;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        font-size: 1.3em;
    }

    /* --- 入力欄 --- */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #c9c3b3 !important;
        background-color: #fff;
        border-radius: 3px;
        padding: 10px !important;
        font-size: 16px;
        color: #3d3d3d;
    }

    /* --- ボタン --- */
    .stButton>button {
        background-color: #a88f59;
        color: white;
        border: 1px solid #a88f59;
        border-radius: 5px;
        font-family: 'Noto Serif JP', serif;
        font-weight: bold;
        letter-spacing: 0.5px;
        padding: 10px 20px;
        font-size: 18px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8c7749;
        border-color: #8c7749;
    }

    /* --- リンク --- */
    a {
        color: #a88f59 !important;
        font-weight: bold;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }

    /* --- expander --- */
    details {
        border: 1px solid #e0d8c0;
        border-radius: 5px;
        padding: 1em;
        margin-bottom: 1em;
    }
    details summary {
        font-weight: bold;
        color: #3d3d3d;
        cursor: pointer;
        list-style: none; /* Remove default arrow */
        padding-bottom: 0.5em;
        border-bottom: 1px dotted #b8b0a0;
    }
    details summary::-webkit-details-marker {
        display: none; /* Hide default arrow Chrome/Safari */
    }
    details summary::before {
        content: '▼ '; /* Custom arrow */
        color: #a88f59;
    }
    details p {
        padding-top: 0.5em;
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
def generate_menu_names(ingredients, request_text):
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
    cleaned_response = response.text.replace("````json", "").replace("`", "").strip()
    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        st.error(f"JSONデコードエラー: {e}\nレスポンス内容: {cleaned_response}")
        return {"main_dish": "提案に失敗しました", "side_dish": "提案に失敗しました"}


def get_recipe_details(dish_name):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    あなたはプロの料理家です。「{dish_name}」の作り方を、以下のフォーマットで、具体的かつ分かりやすく記述してください。

    **材料:**
    - 材料1 (分量)
    - 材料2 (分量)

    **作り方:**
    1. 手順1
    2. 手順2
    3. 手順3
    """
    response = model.generate_content(prompt)
    return response.text

def create_search_link(dish_name):
    query = f"{dish_name} レシピ"
    return f"[https://www.google.com/search?q=](https://www.google.com/search?q=){quote_plus(query)}"

# --- Streamlitの画面表示 ---
st.title('AI Chef\'s Special Menu')
st.write("お客様の食材とご要望を元に、AIシェフが特別な献立と作り方をご提案いたします。")

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
        try:
            with st.spinner('シェフがインスピレーションを得ています... 📜'):
                menu = generate_menu_names(ingredients, user_request)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

            st.header("本日のおすすめ")

            if main_dish_name:
                with st.spinner(f'「{main_dish_name}」のレシピを準備しています...'):
                    main_recipe_details = get_recipe_details(main_dish_name)

                with st.expander(f"主菜： {main_dish_name}", expanded=True):
                    st.markdown(main_recipe_details, unsafe_allow_html=True)
                    st.markdown(f"**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(main_dish_name)})", unsafe_allow_html=True)

            if side_dish_name:
                with st.spinner(f'「{side_dish_name}」のレシピを準備しています...'):
                    side_recipe_details = get_recipe_details(side_dish_name)

                with st.expander(f"副菜： {side_dish_name}", expanded=True):
                    st.markdown(side_recipe_details, unsafe_allow_html=True)
                    st.markdown(f"**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(side_dish_name)})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"申し訳ございません、エラーが発生いたしました: {e}")
            st.error("AIシェフが応答できませんでした。もう一度お試しください。")
