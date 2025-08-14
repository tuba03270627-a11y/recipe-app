import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの献立提案", page_icon="🍽️", layout="wide")

# --- デザイン（CSS） ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500&family=Playfair+Display:wght@700&display=swap');

    /* ページ全体の背景とフォント */
    .stApp {
        background-color: #fdfdfd; /* クリーンな白 */
        font-family: 'Noto Sans JP', sans-serif; /* 日本語に適したモダンなフォント */
    }

    /* タイトル */
    h1 {
        font-family: 'Playfair Display', serif; /* 高級感のあるセリフ体フォント */
        color: #2c3e50; /* 落ち着いたダークブルー */
        text-align: center;
        padding-bottom: 0.5em;
    }
    
    /* 説明文 */
    .st-emotion-cache-1yycg8b p {
        text-align: center;
        color: #7f8c8d;
    }

    /* テキスト入力とテキストエリア */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #bdc3c7 !important;
        border-radius: 8px;
        padding: 12px !important;
        font-size: 16px;
        color: #2c3e50;
    }

    /* ボタン */
    .stButton>button {
        background-color: #2c3e50; /* ダークブルー */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 28px;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        font-size: 16px;
        margin-top: 1em;
    }
    .stButton>button:hover {
        background-color: #34495e;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    /* 結果表示のヘッダー */
    h2 {
        color: #2c3e50;
        font-family: 'Playfair Display', serif;
        text-align: center;
        margin-top: 2em;
    }

    /* 結果表示のカード */
    .st-emotion-cache-1r6slb0 {
        background-color: #ffffff;
        border: 1px solid #ecf0f1;
        border-radius: 10px;
        padding: 1.5em !important;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
    }
    
    /* 結果の小見出し（料理名） */
    h3 {
        color: #34495e;
        border-bottom: 2px solid #34495e;
        padding-bottom: 0.3em;
    }

    /* リンク */
    a {
        color: #3498db !important; /* 明るい青 */
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        color: #2980b9 !important;
        text-decoration: underline;
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
    あなたは一流レストランのシェフです。以下の【使用する食材】を創造的に活かし、【ユーザーの希望】に沿った、洗練された献立（主菜1品、副菜1品）を考えてください。
    回答は、必ず以下のJSONフォーマットで、料理名のみを返してください。説明や挨拶は絶対に含めないでください。
    {{
      "main_dish": "主菜の料理名",
      "side_dish": "副菜の料理名"
    }}
    ---
    【ユーザーの希望】
    {request_text if request_text else "シェフのおまかせ"}

    【使用する食材】
    {ingredients}
    """
    response = model.generate_content(prompt)
    cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

# --- Streamlitの画面表示 ---
st.title('AIシェフの献立提案')
st.write("使いたい食材と、どんな料理が食べたいかの希望を入力してください。AIがあなただけの特別な献立を提案します。")

# --- UI（入力部分） ---
ingredients = st.text_area('使いたい食材をスペースやカンマで区切って入力してください', placeholder='例: 鶏もも肉、パプリカ、玉ねぎ、白ワイン')
user_request = st.text_input('希望はありますか？（任意）', placeholder='例: 洋風で、ワインに合う感じ')

# --- 検索実行と結果表示 ---
if st.button('献立を考えてもらう！', use_container_width=True):
    if not api_key:
        st.error("APIキーが設定されていません。左のサイドバーから入力してください。")
    elif not ingredients:
        st.info('まずは使いたい食材を入力してくださいね。')
    else:
        with st.spinner('AIシェフがインスピレーションを得ています... 👨‍🍳'):
            try:
                menu = generate_menu(ingredients, user_request)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

                st.header("本日の特別な献立はこちらです")
                
                # --- 結果表示をカード風に ---
                with st.container(border=True):
                    st.subheader(f"主菜： {main_dish_name or '提案なし'}")
                    if main_dish_name:
                        st.markdown(f"▶ **[作り方をウェブで探す]({create_search_link(main_dish_name)})**")

                with st.container(border=True):
                    st.subheader(f"副菜： {side_dish_name or '提案なし'}")
                    if side_dish_name:
                        st.markdown(f"▶ **[作り方をウェブで探す]({create_search_link(side_dish_name)})**")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.error("AIからの回答を解析できませんでした。もう一度お試しください。")
