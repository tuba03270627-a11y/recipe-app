import streamlit as st
import requests

def search_and_score_recipes(app_id, keywords_string=""):
    """
    レシピを検索し、キーワードとの一致度でスコアリングして並び替える関数
    """
    # 検索の「きっかけ」として、入力されたキーワード全体をAPIに投げる
    params = {
        'applicationId': app_id,
        'format': 'json',
        'keyword': keywords_string,
        'elements': 'recipeTitle,recipeUrl,recipeMaterial,recipeDescription,cookingTime'
    }
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    
    response = requests.get(request_url, params=params)
    data = response.json()
    recipes_from_api = data.get('result', [])
    
    # スコアリング処理
    scored_recipes = []
    keywords = keywords_string.split()
    if not keywords:
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
st.write("使いたい食材を入力すると、関連性の高い順にレシピを提案します。")

# アプリIDはここに直接入力してください
APPLICATION_ID = '1076379325522336288' 

# --- UI部分 ---
search_keyword = st.text_input(
    '使いたい食材をスペースで区切って入力してください',
    placeholder='例: 豚肉 玉ねぎ 人参'
)

if st.button('レシピを検索！'):
    if search_keyword:
        recipes = search_and_score_recipes(APPLICATION_ID, search_keyword)
        
        if recipes:
            st.success("関連性の高い順にレシピを表示します！")
            for recipe in recipes[:10]: # 上位10件を表示
                st.subheader(recipe.get('recipeTitle', ''))
                st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
                # 材料リストをきれいに表示
                materials_str = "、".join(recipe.get('recipeMaterial', []))
                st.write(f"**材料:** {materials_str}")
                st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '')})")
                st.markdown("---")
        else:
            st.warning("その食材に合うレシピは見つかりませんでした。")
    else:
        st.info('まずは使いたい食材を入力してくださいね。')
