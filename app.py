import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの献立提案", page_icon="🧑‍🍳", layout="centered")

# --- デザイン（CSS）---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

    /* 全体のフォントと背景 */
    .stApp {
        background-color: #f0f2f6; /* 明るいグレー */
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* メインコンテンツのコンテナ */
    .main .block-container {
        max-width: 720px;
        padding: 2rem 2rem;
        background-color: #f0f2f6; /* 背景色と同じにして一体感を出す */
        border-radius: 10px;
        box-shadow: none;
    }

    /* タイトル */
    h1 {
        color: #2a3b4c; /* ディープブルー */
        text-align: center;
        font-weight: 700;
    }
    
    /* 説明文 */
    .st-emotion-cache-1yycg8b p {
        text-align: center;
        color: #52616b;
    }

    /* 入力欄 */
    .stTextArea textarea, .stTextInput>div>div>input {
        background-color: #ffffff;
        border: 1px solid #d0d7de;
        border-radius: 8px;
        color: #2a3b4c;
    }

    /* ボタン */
    .stButton>button {
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.3);
    }
    
    /* 結果表示のヘッダー */
    h2 {
        text-align: center;
        color: #2a3b4c;
        font-weight: 700;
        margin-top: 2em;
    }
    
    /* 結果表示のカード（Expander） */
    details {
        background-color: #ffffff;
        border: 1px solid #d0d7de;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    details summary {
        font-weight: 700;
        color: #2a3b4c;
        cursor: pointer;
    }
    details summary::-webkit-details-marker {
        color: #4facfe;
    }
    
    /* リンク */
    a {
        color: #007bff !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
        color: #0056b3 !important;
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
    あなたはプロの料理家です。以下の【使用する食材】を創造的に活かし、【ユーザーの希望】に沿った、現代的で美味しい献立（主菜1品、副菜1品）を考えてください。
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
    return f"https://www.google.com/search?q={quote_plus(query)}"

# --- Streamlitの画面表示 ---
st.title('🧑‍🍳 AIシェフの献立提案')
st.write("使いたい食材と、どんな料理が食べたいかの希望を入力してください。AIがあなただけの特別な献立を提案します。")

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
            with st.spinner('AIシェフが献立を考案中です...'):
                menu = generate_menu_names(ingredients, user_request)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

            st.header("本日の献立案はこちらです")
            
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
