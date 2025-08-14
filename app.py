import streamlit as st
import requests

# ジャンル名と楽天APIのカテゴリIDを対応させる辞書
# "0"は「こだわらない」= 全ジャンル対象
GENRE_MAP = {
    "こだわらない": "0",
    "和食": "30",
    "洋食": "31",
    "中華": "32",
    "韓国料理": "34",
    "イタリアン": "33",
    "フレンチ": "35",
    "エスニック": "36",
    "麺類": "25",
    "ごはんもの": "14",
    "サラダ": "12",
}

def search_recipe(keyword, app_id, category_id):
    """
    楽天レシピAPIを使ってレシピを検索する関数
    カテゴリIDでの絞り込み機能を追加
    """
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
        'applicationId': app_id,
        'format': 'json',
        'keyword': keyword,
    }
    # カテゴリが「こだわらない」以外の場合のみ、パラメータに追加
    if category_id != "0":
        params['categoryId'] = category_id
    
    response = requests.get(request_url, params=params)
    data = response.json()
    return data.get('result', [])

# --- ここからがStreamlitの画面設定 ---

st.title('🍳 今日の献立、何にする？')

# ★★★ ここのIDは、あなたのアプリIDのままにしてください ★★★
APPLICATION_ID = '1076379325522336288'

# --- UI（見た目）の作成 ---

# ジャンル選択のドロップダウンメニュー
selected_genre_name = st.selectbox('お料理のジャンルを選んでね', list(GENRE_MAP.keys()))
# 選択されたジャンル名からカテゴリIDを取得
selected_category_id = GENRE_MAP[selected_genre_name]

# 食材入力のテキストボックス
search_keyword = st.text_input('冷蔵庫にある食材を入力してください（例：豚肉 玉ねぎ）')

# 検索ボタン
if st.button('レシピを検索！'):
    if search_keyword:
        # 入力されたキーワードと選択されたジャンルでレシピを検索
        recipes = search_recipe(search_keyword, APPLICATION_ID, selected_category_id)

        if recipes:
            st.success(f"「{search_keyword}」の検索結果が見つかりました！")
            for recipe in recipes:
                st.subheader(recipe.get('recipeTitle', '情報なし'))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(recipe.get('recipeDescription', ''))
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---")
        else:
            st.warning('その条件に合うレシピは見つかりませんでした。別の食材やジャンルで試してみてください。')
    else:
        st.info('食材を入力してから検索してくださいね。')
