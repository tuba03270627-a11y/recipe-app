import streamlit as st
import google.generativeai as genai
import json
from urllib.parse import quote_plus

# --- アプリの基本設定 ---
st.set_page_config(page_title="AIシェフの献立提案", page_icon="🍳")

# ジャンルの選択肢を定義
GENRES = ["ジャンルを問わない", "和食", "洋食", "中華", "イタリアン", "韓国料理", "エスニック"]

# --- APIキーの設定 ---
# Streamlit CloudのSecretsからAPIキーを安全に読み込む
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.sidebar.error("StreamlitのSecretsにAPIキーが設定されていません。")
    # ローカルテスト用に、サイドバーからの入力も可能にしておく
    api_key_input = st.sidebar.text_input("または、ここにAPIキーを直接入力:", type="password")
    if api_key_input:
        api_key = api_key_input

if api_key:
    genai.configure(api_key=api_key)

# --- 関数定義 ---
def create_search_link(dish_name):
    """料理名からGoogle検索用のURLを生成する"""
    query = f"{dish_name} レシピ"
    return f"https://www.google.com/search?q={quote_plus(query)}"

def generate_menu(ingredients, genre):
    """AIに献立を考えてもらう関数"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    genre_instruction = f"ジャンルは「{genre}」でお願いします。" if genre != "ジャンルを問わない" else "ジャンルは問いません。"

    prompt = f"""
    あなたはプロの料理家です。以下の【使用する食材】を活かし、【ジャンル】に沿った献立（主菜1品、副菜1品）を考えてください。
    回答は、必ず以下のJSONフォーマットで、料理名のみを返してください。説明や挨拶は絶対に含めないでください。
    {{
      "main_dish": "主菜の料理名",
      "side_dish": "副菜の料理名"
    }}
    ---
    【ジャンル】
    {genre_instruction}

    【使用する食材】
    {ingredients}
    """
    
    response = model.generate_content(prompt)
    cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

# --- Streamlitの画面表示 ---
st.title('🍳 AIシェフの献立提案')
st.write("使いたい食材と希望のジャンルを選ぶと、AIが献立を考え、ウェブ上のレシピをすぐに検索できるようにします。")

# --- UI（入力部分） ---
selected_genre = st.selectbox("お料理のジャンルを選んでください", GENRES)
ingredients = st.text_area('使いたい食材をスペースやカンマで区切って入力してください', placeholder='例: 豚肉 玉ねぎ 人参 卵')

# --- 検索実行と結果表示 ---
if st.button('献立を考えてもらう！'):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif not ingredients:
        st.info('まずは使いたい食材を入力してくださいね。')
    else:
        with st.spinner('AIシェフが腕によりをかけて考案中です... 🍳'):
            try:
                menu = generate_menu(ingredients, selected_genre)
                main_dish_name = menu.get("main_dish")
                side_dish_name = menu.get("side_dish")

                st.header("本日の献立案はこちらです！")

                if main_dish_name:
                    st.subheader(f"主菜： {main_dish_name}")
                    st.markdown(f"▶ **[このレシピの作り方をウェブで検索する]({create_search_link(main_dish_name)})**")
                
                st.markdown("---")

                if side_dish_name:
                    st.subheader(f"副菜： {side_dish_name}")
                    st.markdown(f"▶ **[このレシピの作り方をウェブで検索する]({create_search_link(side_dish_name)})**")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.error("AIからの回答を解析できませんでした。サーバーが混み合っているか、予期せぬ形式で返ってきた可能性があります。少し待ってから、もう一度試してみてください。")


