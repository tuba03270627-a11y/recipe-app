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

    /* ★★★ ここが背景の変更点 ★★★ */
    .stApp {
        background-color: #4a3c31; /* 深いブラウン */
        background-image: url("https://www.transparenttextures.com/patterns/old-paper.png");
        background-attachment: fixed;
        background-size: cover;
    }

    /* ★★★ 全体のフォントと文字色の変更点 ★★★ */
    body, .st-emotion-cache-1qg05j3, .st-emotion-cache-1yycg8b p {
        font-family: 'Cormorant Garamond', serif; 
        color: #e3dcd2; /* 明るいクリーム色 */
        font-size: 18px;
    }

    /* --- メインコンテンツのコンテナ（メニュー用紙）--- */
    .main .block-container {
        max-width: 800px; padding: 2.5rem; background-color: rgba(253, 251, 243, 0.95); /* 背景をより不透明に */
        border: 1px solid #d4c8b8; border-radius: 2px; box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }
    
    /* --- タイトル --- */
    h1 {
        font-family: 'Playfair Display', serif; font-style: italic; color: #8c7853; text-align: center;
        border-bottom: 2px double #d4c8b8; padding-bottom: 0.5em; margin-bottom: 1.5em; font-size: 3em;
    }
    
    /* 入力欄の文字は濃いままにする */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #d4c8b8 !important; background-color: #fff; color: #5a483a !important;
    }

    /* --- ボタン --- */
    .stButton>button {
        background-color: #8c7853; color: white; border: 1px solid #8c7853; border-radius: 2px;
        font-family: 'Cormorant Garamond', serif; font-weight: bold; letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #7a6843; border-color: #7a6843;
    }
    
    /* --- 結果表示 --- */
    h2 {
        text-align: center; color: #8c7853; font-family: 'Playfair Display', serif; font-style: italic;
        margin-top: 2em; font-size: 2.2em;
    }
    h3 {
        color: #5a483a; font-weight: bold; border: none; text-align: center;
        margin-top: 1.5em; letter-spacing: 0.5px;
    }
    a { color: #8c7853 !important; font-weight: bold; }
    .st-emotion-cache-1r6slb0 { /* 結果表示コンテナの余白などをリセット */
        background-color: transparent; border: none; padding: 0 !important;
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
    """AIに献立名を考えてもらう関数"""
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

            st.header("本日の一皿")
            
            if main_dish_name:
                with st.spinner(f'「{main_dish_name}」のレシピを準備しています...'):
                    main_recipe_details = get_recipe_details(main_dish_name)
                
                with st.expander(f"主菜： {main_dish_name}", expanded=True):
                    st.markdown(main_recipe_details)
                    st.markdown(f"**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(main_dish_name)})", unsafe_allow_html=True)
            
            if side_dish_name:
                with st.spinner(f'「{side_dish_name}」のレシピを準備しています...'):
                    side_recipe_details = get_recipe_details(side_dish_name)

                with st.expander(f"副菜： {side_dish_name}", expanded=True):
                    st.markdown(side_recipe_details)
                    st.markdown(f"**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(side_dish_name)})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"申し訳ございません、エラーが発生いたしました: {e}")
            st.error("AIシェフが応答できませんでした。もう一度お試しください。")
