import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

st.markdown(
    """
    <style>
    /* ページ全体の背景と文字色 */
    .stApp {
        background-color: #F5F5F5; /* 上品なオフホワイト */
    }

    /* メインコンテンツの文字色 */
    body {
        color: #363636; /* ダークグレー */
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
    }

    /* タイトルのスタイル */
    h1 {
        color: #DAA520; /* ゴールド */
        font-family: 'Garamond', serif;
        text-align: center;
        border-bottom: 2px solid #DAA520;
        padding-bottom: 10px;
    }

    /* 入力欄のラベル */
    .st-emotion-cache-1qg05j3 {
        color: #363636 !important;
        font-weight: bold;
    }
    
    /* ボタンのスタイル */
    .stButton>button {
        background-color: #363636; /* ダークグレー */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #DAA520;
        color: #363636;
        transform: translateY(-2px);
    }

    /* 結果表示のカード */
    .st-emotion-cache-1r6slb0 {
        background-color: white;
        border-radius: 10px;
        padding: 2em !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* 結果の小見出し */
    h3 {
        color: #363636;
        border-left: 5px solid #DAA520;
        padding-left: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの献立提案", page_icon="🍳", layout="wide")

# --- APIキーの設定 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.sidebar.warning("デプロイする際は、Streamlitのシークレット機能でAPIキーを設定してください。")
    api_key = st.sidebar.text_input("ここにGoogle AI StudioのAPIキーを貼り付けてください:", type="password", key="api_key_input")

if api_key:
    genai.configure(api_key=api_key)

# --- 関数定義 ---
def create_search_link(dish_name):
    """料理名からGoogle検索用のURLを生成する"""
    query = f"{dish_name} レシピ"
    return f"https://www.google.com/search?q={quote_plus(query)}"

def generate_menu(ingredients, request_text):
    """AIに献立を考えてもらう関数"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    あなたはプロの料理家です。以下の【使用する食材】をなるべく使いつつ、【ユーザーの希望】に沿った献立（主菜1品、副菜1品）を考えてください。
    回答は、必ず以下のJSONフォーマットで、料理名のみを返してください。説明や挨拶は絶対に含めないでください。
    {{
      "main_dish": "主菜の料理名",
      "side_dish": "副菜の料理名"
    }}
    ---
    【ユーザーの希望】
    {request_text if request_text else "特になし"}

    【使用する食材】
    {ingredients}
    """
    
    response = model.generate_content(prompt)
    cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

# --- Streamlitの画面表示 ---
st.title('🍳 AIシェフの献立提案')
st.write("使いたい食材と、どんな料理が食べたいかの希望を入力してください。AIがあなただけの献立を提案します。")

# --- UI（入力部分） ---
# ★★★ UI改善点①：2列レイアウト ★★★
col1, col2 = st.columns(2)
with col1:
    ingredients = st.text_area('使いたい食材をスペースやカンマで区切って入力してください', placeholder='例: 豚肉 玉ねぎ 人参 卵')
with col2:
    user_request = st.text_input('希望はありますか？（任意）', placeholder='例: 中華で、さっぱりしたもの')

# --- 検索実行と結果表示 ---
if st.button('献立を考えてもらう！', use_container_width=True):
    if not api_key:
        st.error("APIキーを設定してください。サイドバーから入力できます。")
    elif not ingredients:
        st.info('まずは使いたい食材を入力してくださいね。')
    else:
        with st.spinner('AIシェフが腕によりをかけて考案中です... 🍳'):
            try:
                menu = generate_menu(ingredients, user_request)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

                st.header("本日の献立案はこちらです！")
                
                # ★★★ UI改善点②：結果表示も2列レイアウト ★★★
                res_col1, res_col2 = st.columns(2)

                with res_col1:
                    # ★★★ UI改善点③：カード風の表示 ★★★
                    with st.container(border=True):
                        st.subheader(f"主菜： {main_dish_name or '提案なし'}")
                        if main_dish_name:
                            st.markdown(f"▶ **[作り方をウェブで検索する]({create_search_link(main_dish_name)})**")

                with res_col2:
                    with st.container(border=True):
                        st.subheader(f"副菜： {side_dish_name or '提案なし'}")
                        if side_dish_name:
                            st.markdown(f"▶ **[作り方をウェブで検索する]({create_search_link(side_dish_name)})**")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.error("AIからの回答を解析できませんでした。もう一度試してみてください。")
