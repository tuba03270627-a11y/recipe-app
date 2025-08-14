import streamlit as st
import requests

# 親子関係を持つカテゴリのデータ構造を定義
RECIPE_CATEGORIES = {
    "ジャンルを問わない": {
        "すべて": "0" # "0"は全カテゴリを意味する
    },
    "和食": {
        "すべて": "30",
        "肉料理": "30-274",
        "魚料理": "30-275",
        "ごはんもの": "14-143",
        "麺類": "25-250", # うどん・そばなど
    },
    "洋食": {
        "すべて": "31",
        "肉料理": "31-279",
        "魚料理": "31-280",
        "ごはんもの": "14-144",
        "パスタ": "15-364",
    },
    "中華": {
        "すべて": "32",
        "肉料理": "32-283",
        "ごはんもの・麺類": "14-145",
        "炒め物": "32-284",
    },
    # 必要に応じて他のジャンルも追加可能
}


def search_recipe(keyword, app_id, category_id):
    """
    指定されたカテゴリIDとキーワードでレシピを検索する関数
    """
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
        'applicationId': app_id,
        'format': 'json',
        'keyword': keyword,
    }
    # カテゴリIDが"0"（すべて）でない場合のみ、パラメータに追加
    if category_id != "0":
        params['categoryId'] = category_id
    
    response = requests.get(request_url, params=params)
    data = response.json()
    
    # タイトルと材料リストの両方をチェックするフィルタリング
    recipes_from_api = data.get('result', [])
    filtered_recipes = []
    keywords = keyword.split()
    
    for recipe in recipes_from_api:
        title = recipe.get('recipeTitle', '')
        materials = " ".join(recipe.get('recipeMaterial', []))
        search_target = title + materials

        if all(kw in search_target for kw in keywords):
            filtered_recipes.append(recipe)
    
    return filtered_recipes

# --- Streamlitの画面設定 ---

st.title('🍳 今日の献立、何にする？')

APPLICATION_ID = '1076379325522336288'

# --- 2段階のカテゴリ選択UI ---

# 1. 親カテゴリ（ジャンル）の選択
selected_genre = st.selectbox(
    "大まかなジャンルを選んでください",
    list(RECIPE_CATEGORIES.keys())
)

# 2. 親カテゴリの選択に応じて、子カテゴリの選択肢を動的に変更
sub_categories = RECIPE_CATEGORIES[selected_genre]
selected_sub_category_name = st.selectbox(
    "具体的な種類を選んでください",
    list(sub_categories.keys())
)

# --- 食材入力と検索ボタン ---

search_keyword = st.text_input('冷蔵庫にある食材を入力してください（例：豚肉 玉ねぎ）')

if st.button('レシピを検索！'):
    if search_keyword:
        # 選択されたジャンルと種類から、最終的なカテゴリIDを取得
        category_id_to_search = sub_categories[selected_sub_category_name]
        
        st.info(f"「{selected_genre}」の「{selected_sub_category_name}」から、「{search_keyword}」を使ったレシピを探します...")
        
        recipes = search_recipe(search_keyword, APPLICATION_ID, category_id_to_search)
        
        if recipes:
            st.success("レシピが見つかりました！")
            for recipe in recipes[:5]: # 候補を5つに絞って表示
                st.subheader(recipe.get('recipeTitle', '情報なし'))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(f"**説明:** {recipe.get('recipeDescription', '')}")
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---")
        else:
            st.warning("その条件に合うレシピは見つかりませんでした。")
    else:
        st.info('食材を入力してから検索してくださいね。')
