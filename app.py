import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

"""
    <style>
    /* ページ全体の背景 */
    .stApp {
        background-color: #f8f8f8; /* より明るい背景 */
    }

    /* メインコンテンツの文字色 */
    body {
        color: #333; /* より濃い文字色 */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* モダンなフォント */
        -webkit-font-smoothing: antialiased; /* 文字を滑らかに */
    }

    /* タイトル */
    h1 {
        color: #c0a377; /* 上品なゴールド */
        font-family: 'Playfair Display', serif; /* 高級感のあるフォント */
        text-align: center;
        border-bottom: 1px solid #c0a377;
        padding-bottom: 0.5em;
        margin-bottom: 1em;
        font-size: 2.5em;
    }

    /* サブタイトルなど */
    h2, h3, h4, h5, h6 {
        color: #555;
        font-weight: bold;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }

    /* テキスト入力とテキストエリア */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #ddd !important;
        border-radius: 0.5em;
        padding: 0.75em !important;
        font-size: 1em;
    }

    /* ボタン */
    .stButton>button {
        background-color: #333;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 0.5em;
        padding: 0.75em 1.5em !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
        font-size: 1em !important;
    }
    .stButton>button:hover {
        background-color: #c0a377;
        border-color: #c0a377 !important;
        color: #333 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* 結果表示のコンテナ */
    .st-emotion-cache-1r6slb0 {
        background-color: #fff;
        border: 1px solid #eee;
        border-radius: 0.5em;
        padding: 1.5em !important;
        margin-bottom: 1em !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* リンク */
    a {
        color: #c0a377 !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    """
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
