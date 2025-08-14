import streamlit as st
import requests

# 主菜・副菜のカテゴリIDを定義
MAIN_DISH_CATEGORIES = {
    "肉料理": "30",
    "魚料理": "31",
    "ごはんもの": "14",
    "パスタ": "15",
    "麺類": "25",
}

SIDE_DISH_CATEGORIES = {
    "サラダ": "12",
    "スープ・汁物": "13",
    "副菜": "11",
}


def search_recipe(keyword, app_id, category_id):
    """
    指定されたカテゴリIDとキーワードでレシピを検索する関数
    """
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {
        'applicationId': app_id,
        'format': 'json',
        'categoryId': category_id,
        'keyword': keyword,
    }
    
    response = requests.get(request_url, params=params)
    data = response.json()
    
    recipes_from_api = data.get('result', [])
    filtered_recipes = []
    keywords = keyword.split()
    
    for recipe in recipes_from_api:
        # ★★★ ここが改善点！★★★
        # タイトルと材料リストを結合して、検索対象とする
        title = recipe.get('recipeTitle', '')
        # recipeMaterialは文字列のリストなので、空白で連結して一つの文字列にする
        materials = " ".join(recipe.get('recipeMaterial', []))
        search_target = title + materials  # タイトルと材料を合体！

        # 検索キーワードが、合体した検索対象の中にすべて含まれているかチェック
        if all(kw in search_target for kw in keywords):
            filtered_recipes.append(recipe)
    
    return filtered_recipes

# --- Streamlitの画面設定 ---

st.title('🍳 今日の献立、何にする？')

APPLICATION_ID = '1076379325522336288'

search_keyword = st.text_input('冷蔵庫にある食材を入力してください（例：豚肉 玉ねぎ）')

if st.button('献立を検索！'):
    if search_keyword:
        st.info(f"「{search_keyword}」を使った献立を探します...")

        # --- 主菜の検索と表示 ---
        st.header("主菜の候補はこちら")
        main_category_id = f"{MAIN_DISH_CATEGORIES['肉料理']}-{MAIN_DISH_CATEGORIES['魚料理']}"
        main_dishes = search_recipe(search_keyword, APPLICATION_ID, main_category_id)
        
        if main_dishes:
            for recipe in main_dishes[:3]:
                st.subheader(recipe.get('recipeTitle', '情報なし'))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---")
        else:
            st.write("条件に合う主菜が見つかりませんでした。")

        # --- 副菜の検索と表示 ---
        st.header("副菜の候補はこちら")
        side_category_id = f"{SIDE_DISH_CATEGORIES['副菜']}-{SIDE_DISH_CATEGORIES['サラダ']}"
        side_dishes = search_recipe(search_keyword, APPLICATION_ID, side_category_id)

        if side_dishes:
            for recipe in side_dishes[:3]:
                st.subheader(recipe.get('recipeTitle', '情報なし'))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
                st.markdown("---")
        else:
            st.write("条件に合う副菜が見つかりませんでした。")

    else:
        st.info('食材を入力してから検索してくださいね。')
