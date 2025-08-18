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

    /* ★★★ ここからがデザインの最終修正 ★★★ */

    /* ページ全体の背景は明るいまま */
    .stApp {
        background-color: #f5f0e1; /* 薄いベージュ */
    }
    
    /* 基本の文字色（ページ背景に対する色） */
    body, p, label {
        color: #4a4a4a !important;
        font-family: 'Noto Serif JP', serif;
    }

    /* メインのコンテナ（メニューカード）をダークに */
    .main .block-container {
        max-width: 700px;
        padding: 3rem;
        background-color: #2c3e50; /* ダークスレートブルー */
        border: 1px solid #3d2b1f;
        border-radius: 5px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        position: relative;
        color: #e0e0e0 !important; /* ★この中の文字は明るい色に */
    }
    
    /* カードの中の文字色を個別に調整 */
    .main .block-container p, .main .block-container li, .main .block-container .stMarkdown {
        color: #e0e0e0 !important; /* 明るいグレー */
    }

    /* カードの装飾的な枠線 */
    .main .block-container::before {
        content: ''; position: absolute; top: 15px; left: 15px; right: 15px; bottom: 15px;
        border: 2px double rgba(224, 224, 224, 0.5); /* 明るい色の枠線 */
        border-radius: 3px; pointer-events: none;
    }
    
    /* タイトル（カードの外）は濃い色 */
    h1 {
        font-family: 'Playfair Display', serif !important; font-style: italic;
        color: #a88f59 !important;
        text-align: center; padding-bottom: 0.3em; margin-bottom: 1em; font-size: 3.2em;
    }
    
    /* カードの中のサブタイトル */
    .main .block-container h2 {
        color: #d4af37 !important; /* 明るいゴールド */
        font-family: 'Playfair Display', serif !important; font-style: italic;
        text-align: center; margin-top: 1em; margin-bottom: 1.5em;
    }

    /* カードの中の料理名 */
    .main .block-container h3 {
        color: #ffffff !important; /* 白 */
        border-bottom: 1px dotted #888;
        padding-bottom: 0.5em; margin-top: 1.5em;
    }
    
    /* 入力欄 */
    .stTextArea textarea, .stTextInput>div>div>input {
        border: 1px solid #555 !important;
        background-color: #3a506b !important; /* 少し明るいダークブルー */
        border-radius: 3px;
        padding: 10px !important;
        font-size: 16px;
        color: #ffffff !important; /* 入力文字は白 */
    }
    
    /* ボタン */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #d4af37 !important; /* 明るいゴールド */
        color: #2c3e50 !important; /* 濃い文字色 */
        border: 1px solid #d4af37 !important;
        border-radius: 5px !important;
        font-family: 'Noto Serif JP', serif !important;
        font-weight: 700 !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #c8a435 !important;
        border-color: #c8a435 !important;
    }
    
    /* 結果表示（Expander） */
    details {
        border: 1px solid #555;
        border-radius: 5px;
        padding: 1em;
        margin-bottom: 1em;
        background-color: rgba(0,0,0,0.1);
    }
    details summary {
        font-weight: 700;
        font-size: 1.1em;
        cursor: pointer;
        color: #ffffff !important; /* タイトル文字は白 */
    }
    
    /* カードの中のリンク */
    .main .block-container a {
       color: #d4af37 !important;
    }

    /* ★★★ここまでがデザインの最終修正★★★ */
    </style>
    """,
    unsafe_allow_html=True,
)


# --- APIキーの設定 ---
# (変更なし)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.sidebar.info("アプリをデプロイする際は、StreamlitのSecrets機能でAPIキーを設定すると、この欄は表示されなくなります。")
    api_key = st.sidebar.text_input("ここにGoogle AI StudioのAPIキーを貼り付けてください:", type="password", key="api_key_input")

if api_key:
    genai.configure(api_key=api_key)

# --- 関数定義 ---
# (変更なし)
def generate_full_menu(ingredients, request_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    あなたは格式高いレストランのシェフです。以下の【使用する食材】を創造的に活かし、【お客様からのご要望】に沿った献立を考えてください。
    ご要望に品数の指定がない場合は、主菜1品と副菜1品を基本としてください。
    回答は、必ず以下のJSONフォーマットで返してください。説明や挨拶は絶対に含めないでください。
    各料理には、料理名（name）、種類（type）、材料リスト（materials）、作り方の手順リスト（steps）を含めてください。
    {{
      "menu": [
        {{
          "type": "主菜",
          "name": "料理名",
          "materials": ["材料1 (分量)", "材料2 (分量)"],
          "steps": ["手順1", "手順2", "手順3"]
        }},
        {{
          "type": "副菜",
          "name": "料理名",
          "materials": ["材料1 (分量)", "材料2 (分量)"],
          "steps": ["手順1", "手順2"]
        }}
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

def create_search_link(dish_name):
    query = f"{dish_name} レシピ"
    return f"https://www.google.com/search?q={quote_plus(query)}"

# --- Streamlitの画面表示 ---
# (変更なし)
st.title('AI Chef\'s Special Menu')
st.write("お客様の食材とご要望を元に、AIシェフが特別な献立と作り方をご提案いたします。")

with st.form(key='my_form'):
    ingredients = st.text_area('ご使用になる食材をお聞かせください', placeholder='例: 鶏もも肉、パプリカ、玉ねぎ、白ワイン')
    user_request = st.text_input('その他、ご要望はございますか？（任意）', placeholder='例: 3品ほしい。一品は汁物')
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submit_button = st.form_submit_button(label='献立を提案いただく')
    with col2:
        clear_button = st.form_submit_button(label='クリア')

if submit_button:
    if not api_key:
        st.error("恐れ入りますが、先にAPIキーの設定をお願いいたします。")
    elif not ingredients:
        st.info('まずは、ご使用になる食材をお聞かせください。')
    else:
        try:
            with st.spinner('シェフが特別な献立を考案しております... 📜'):
                menu_data = generate_full_menu(ingredients, user_request)
                menu_list = menu_data.get("menu", [])

            st.header("本日のおすすめ")
            
            if not menu_list:
                st.warning("ご要望に沿った献立の提案が難しいようです。条件を変えてお試しください。")
            
            for dish in menu_list:
                dish_type = dish.get("type", "一品")
                dish_name = dish.get("name", "名称不明")
                materials = dish.get("materials", [])
                steps = dish.get("steps", [])

                if dish_name != "名称不明":
                    with st.expander(f"{dish_type}： {dish_name}", expanded=True):
                        st.markdown("**材料:**")
                        for m in materials:
                            st.markdown(f"- {m}")
                        
                        st.markdown("\n**作り方:**")
                        for i, s in enumerate(steps, 1):
                            st.markdown(f"{i}. {s}")
                        
                        st.markdown(f"\n**さらに詳しく** ▷ [*写真付きの作り方をウェブで探す*]({create_search_link(dish_name)})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"申し訳ございません、エラーが発生いたしました: {e}")
            st.error("AIシェフが応答できませんでした。もう一度お試しください。")
