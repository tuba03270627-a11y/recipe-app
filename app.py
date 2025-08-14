import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AI Chef's Special Menu", page_icon="📜", layout="centered")

# --- デザイン（CSS） ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500&family=Playfair+Display:ital,wght@1,700&display=swap');

    /* --- 背景 --- */
    .stApp {
        background-color: #f5f0e1; /* 薄いベージュ */
        background-image: url("https://www.transparenttextures.com/patterns/old-paper.png");
        background-attachment: fixed;
    }

    /* --- メインコンテンツのコンテナ（メニュー用紙）--- */
    .main .block-container {
        max-width: 700px; padding: 3rem; background-color: #fffef8;
        border: 1px solid #d4c8b8; border-radius: 5px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        position: relative;
    }

    /* --- メニュー用紙の装飾的な枠線 --- */
    .main .block-container::before {
        content: ''; position: absolute; top: 15px; left: 15px; right: 15px; bottom: 15px;
        border: 2px double #d8c9b1; border-radius: 3px; pointer-events: none;
    }

    /* --- 全体のフォントと文字色 --- */
    body, p, ol, ul, li {
        font-family: 'Noto Serif JP', serif; color: #4a4a4a; font-size: 17px; line-height: 1.8;
    }

    /* --- タイトル --- */
    h1 {
        font-family: 'Playfair Display', serif; font-style: italic; color: #a88f59; text-align: center;
        padding-bottom: 0.3em; margin-bottom: 1em; font-size: 3.2em; letter-spacing: 1px;
    }
    
    /* --- 説明文 --- */
    .st-emotion-cache-1yycg8b p {
        text-align: center; font-size: 1em;
    }

    /* --- サブタイトル --- */
    h2 {
        text-align: center; color: #a88f59; font-family: 'Playfair Display', serif; font-style: italic;
        margin-top: 2em; margin-bottom: 1.5em; font-size: 2.2em;
    }

    /* --- 料理名 --- */
    h3 {
        color: #3d3d3d; font-weight: 700; border-bottom: 1px dotted #b8b0a0;
        padding-bottom: 0.5em; margin-top: 1.5em; margin-bottom: 1em; font-size: 1.3em;
    }

    /* --- 入力欄 --- */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #c9c3b3 !important; background-color: #fff; border-radius: 3px;
        padding: 10px !important; font-size: 16px; font-family: 'Noto Serif JP', serif; color: #3d3d3d;
    }
    .st-emotion-cache-1qg05j3 { color: #4a4a4a; }

    /* --- ボタン --- */
    .stButton>button {
        background-color: #a88f59; color: white; border: 1px solid #a88f59; border-radius: 5px;
        font-family: 'Noto Serif JP', serif; font-weight: 500; letter-spacing: 1px;
        padding: 12px 24px; font-size: 18px; transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #8c7749; border-color: #8c7749;
    }

    /* --- 結果表示（Expander） --- */
    details {
        border: 1px solid #e0d8c0; border-radius: 5px; padding: 1em; margin-bottom: 1em;
        background-color: rgba(255,255,255,0.3);
    }
    details summary {
        font-weight: 700; font-size: 1.1em; color: #3d3d3d; cursor: pointer;
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
    """AIに献立名を考えてもらう関数（可変長対応）"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # ★★★ ここが改善点！AIへのお願いを柔軟に変更 ★★★
    prompt = f"""
    あなたは格式高いレストランのシェフです。以下の【使用する食材】を創造的に活かし、【お客様からのご要望】に沿った献立を考えてください。
    ご要望に品数の指定がない場合は、主菜1品と副菜1品を基本としてください。
    回答は、必ず以下のJSONフォーマットで返してください。説明や挨拶は絶対に含めないでください。
    {{
      "menu": [
        {{ "type": "（主菜、副菜、汁物など）", "name": "料理名" }},
        {{ "type": "（主菜、副菜、汁物など）", "name": "料理名" }}
      ]
    }}
    ---
    【お客様からのご要望】
    {request_text if request_text else "シェフのおまかせ（主菜と副菜）"}

    【使用する食材】
    {ingredients}
    """
    response = model.generate_content(prompt)
    cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

def get_recipe_details(dish_name):
    """AIに特定の料理のレシピを教えてもらう関数"""
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
    """料理名からGoogle検索用のURLを生成する関数"""
    query = f"{dish_name} レシピ"
    return f"https://www.google.com/search?q={quote_plus(query)}"

# --- Streamlitの画面表示 ---
st.title('AI Chef\'s Special Menu')
st.write("お客様の食材とご要望を元に、AIシェフが特別な献立と作り方をご提案いたします。")

# --- UI（入力部分） ---
ingredients = st.text_area('ご使用になる食材をお聞かせください', placeholder='例: 鶏もも肉、パプリカ、玉ねぎ、白ワイン')
user_request = st.text_input('その他、ご要望はございますか？（任意）', placeholder='例: 3品ほしい。一品は汁物')

# --- 検索実行と結果表示 ---
if st.button('献立を提案いただく', use_container_width=True):
    if not api_key:
        st.error("恐れ入りますが、先にAPIキーの設定をお願いいたします。")
    elif not ingredients:
        st.info('まずは、ご使用になる食材をお聞かせください。')
    else:
        try:
            with st.spinner('シェフがインスピレーションを得ています... 📜'):
                menu_data = generate_menu_names(ingredients, user_request)
                menu_list = menu_data.get("menu", [])

            st.header("本日のおすすめ")
            
            # ★★★ ここが改善点！リストの品数だけループして表示 ★★★
            if not menu_list:
                st.warning("ご要望に沿った献立の提案が難しいようです。条件を変えてお試しください。")
            
            for dish in menu_list:
                dish_type = dish.get("type", "一品")
                dish_name = dish.get("name", "名称不明")

                if dish_name != "名称不明":
                    with st.spinner(f'「{dish_name}」のレシピを準備しています...'):
                        recipe_details = get_recipe_details(dish_name)
                    
                    with st.expander(f"{dish_type}： {dish_name}", expanded=True):
                        st.markdown(recipe_details, unsafe_allow_html=True)
                        st.markdown(f"**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(dish_name)})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"申し訳ございません、エラーが発生いたしました: {e}")
            st.error("AIシェフが応答できませんでした。もう一度お試しください。")
