import streamlit as st
import requests

# --- この部分は今までのコードとほぼ同じ ---
def search_recipe(keyword, app_id):
    """
    楽天レシピAPIを使ってレシピを検索する関数
    """
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
        'applicationId': app_id,
        'format': 'json',
        'keyword': keyword,
    }
    response = requests.get(request_url, params=params)
    data = response.json()
    return data.get('result', []) # resultがない場合は空のリストを返す

# --- ここからがStreamlitの魔法 ---

# 1. アプリのタイトルを設定
st.title('🍳 今日の献立、何にする？')

# 2. アプリIDと検索キーワードの入力欄を作成
# ★★★ ここのIDは、あなたのアプリIDに書き換えてください ★★★
APPLICATION_ID = '1076379325522336288'
search_keyword = st.text_input('冷蔵庫にある食材を入力してください（例：豚肉 玉ねぎ）')

# 3. 検索ボタンを作成
if st.button('レシピを検索！'):
    if search_keyword:
        # 入力されたキーワードでレシピを検索
        recipes = search_recipe(search_keyword, APPLICATION_ID)

        if recipes:
            st.success(f"「{search_keyword}」の検索結果が見つかりました！")
            # 検索結果を1つずつ表示
            for recipe in recipes:
                st.subheader(recipe.get('recipeTitle', '情報なし')) # 料理名を少し大きく表示
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(recipe.get('recipeDescription', ''))
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---") # 区切り線
        else:
            st.warning('その食材に合うレシピは見つかりませんでした。別の食材で試してみてください。')
    else:
        st.info('食材を入力してから検索してくださいね。')
