import streamlit as st
import requests

# 主菜・副菜のカテゴリIDを定義
MAIN_DISH_CATEGORIES = "30-31-14-15-25" # 肉,魚,ごはん,パスタ,麺
SIDE_DISH_CATEGORIES = "11-12-13"      # 副菜,サラダ,スープ

def search_and_score_recipes(app_id, category_id, keywords_string=""):
    """
    指定カテゴリ内でレシピを検索し、キーワードとの一致度でスコアリングして返す
    """
    params = {
        'applicationId': app_id,
        'format': 'json',
        'categoryId': category_id,
        'elements': 'recipeTitle,recipeUrl,recipeMaterial,recipeDescription,cookingTime'
    }
    # 検索の「きっかけ」として、入力されたキーワードの最初の単語だけをAPIに渡す
    keywords = keywords_string.split()
    if keywords:
        params['keyword'] = keywords[0]

    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    response = requests.get(request_url, params=params)
    data = response.json()
    recipes_from_api = data.get('result', [])
    
    # スコアリング処理
    scored_recipes = []
    if not keywords: # キーワードがなければ空のリストを返す
        return []

    for recipe in recipes_from_api:
        score = 0
        title = recipe.get('recipeTitle', '')
        materials = " ".join(recipe.get('recipeMaterial', []))
        search_target = title + materials
        
        for kw in keywords:
            if kw in search_target:
                score += 1
        
        if score > 0:
            scored_recipes.append({'recipe': recipe, 'score': score})
    
    # スコアの高い順に並び替え
    sorted_by_score = sorted(scored_recipes, key=lambda x: x['score'], reverse=True)
    return [item['recipe'] for item in sorted_by_score]

# --- Streamlitの画面設定 ---
st.title('🍳 今日の献立、何にする？')
st.write("使いたい食材を入力すると、主菜と副菜の献立を提案します。")

APPLICATION_ID = '1076379325522336288' 

# --- UI部分 ---
search_keyword = st.text_input(
    '使いたい食材をスペースで区切って入力してください',
    placeholder='例: 豚肉 玉ねぎ 人参'
)

if st.button('献立を提案してもらう！'):
    if search_keyword:
        # --- 主菜の検索 ---
        main_dishes = search_and_score_recipes(APPLICATION_ID, MAIN_DISH_CATEGORIES, search_keyword)
        
        # --- 副菜の検索 ---
        side_dishes = search_and_score_recipes(APPLICATION_ID, SIDE_DISH_CATEGORIES, search_keyword)

        # --- 結果の表示 ---
        st.header("本日の献立案")

        if main_dishes:
            st.subheader("主菜はこちら")
            main_dish = main_dishes[0] # 最もスコアの高いものを1つ提案
            st.write(f"**{main_dish.get('recipeTitle', '')}**")
            materials_str = "、".join(main_dish.get('recipeMaterial', []))
            st.write(f"**材料:** {materials_str}")
            st.write(f"🔗 [作り方を見る]({main_dish.get('recipeUrl', '')})")
        else:
            st.warning("条件に合う主菜が見つかりませんでした。")
        
        st.markdown("---")

        if side_dishes:
            st.subheader("副菜はこちら")
            side_dish = side_dishes[0] # 最もスコアの高いものを1つ提案
            st.write(f"**{side_dish.get('recipeTitle', '')}**")
            materials_str = "、".join(side_dish.get('recipeMaterial', []))
            st.write(f"**材料:** {materials_str}")
            st.write(f"🔗 [作り方を見る]({side_dish.get('recipeUrl', '')})")
        else:
            st.warning("条件に合う副菜が見つかりませんでした。")

    else:
        st.info('まずは使いたい食材を入力してくださいね。')
