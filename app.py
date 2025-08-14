import streamlit as st
import requests

# ジャンル名と楽天APIのカテゴリIDを対応させる辞書
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
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
        'applicationId': app_id,
        'format': 'json',
        'keyword': keyword,
    }
    if category_id != "0":
        params['categoryId'] = category_id
    
    response = requests.get(request_url, params=params)
    data = response.json()
    return data.get('result', [])

st.title('🍳 今日の献立、何にする？')

# ★★★ ここのIDは、あなたのアプリIDのままにしてください ★★★
APPLICATION_ID = '1076379325522336288'

# --- UI（見た目）の作成 ---

selected_genre_name = st.selectbox('お料理のジャンルを選んでね', list(GENRE_MAP.keys()))
selected_category_id = GENRE_MAP[selected_genre_name]

search_keyword = st.text_input('冷蔵庫にある食材を入力してください（例：豚肉 玉ねぎ）')

if st.button('レシピを検索！'):
    if search_keyword:
        # 1. まずAPIにレシピを問い合わせる
        recipes_from_api = search_recipe(search_keyword, APPLICATION_ID, selected_category_id)
        
        # 2. ★★★ ここからが新しい処理 ★★★
        # APIから返ってきた結果を、さらにプログラムで絞り込む
        truly_filtered_recipes = []
        keywords = search_keyword.split() # 検索キーワードを空白で区切ってリストにする

        for recipe in recipes_from_api:
            title = recipe.get('recipeTitle', '')
            # all()を使って、全てのキーワードがタイトルに含まれているかチェック
            if all(kw in title for kw in keywords):
                truly_filtered_recipes.append(recipe)
        
        # 3. 最終的に絞り込んだ結果を表示する
        if truly_filtered_recipes:
            st.success(f"「{search_keyword}」の検索結果が見つかりました！")
            for recipe in truly_filtered_recipes:
                st.subheader(recipe.get('recipeTitle', '情報なし'))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(recipe.get('recipeDescription', ''))
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---")
        else:
            st.warning('その条件に合うレシピは見つかりませんでした。別の食材やジャンルで試してみてください。')
    else:
        st.info('食材を入力してから検索してくださいね。')
