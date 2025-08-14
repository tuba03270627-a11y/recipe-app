import streamlit as st
import requests

# (カテゴリ定義は変更なし)
RECIPE_CATEGORIES = {
    "ジャンルを問わない": {"すべて": "0"},
    "和食": {"すべて": "30", "肉料理": "30-274", "魚料理": "30-275", "ごはんもの": "14-143", "麺類": "25-250"},
    "洋食": {"すべて": "31", "肉料理": "31-279", "魚料理": "31-280", "ごはんもの": "14-144", "パスタ": "15-364"},
    "中華": {"すべて": "32", "肉料理": "32-283", "ごはんもの・麺類": "14-145", "炒め物": "32-284"},
}

def search_and_score_recipes(app_id, category_id, keywords_string=""):
    """
    レシピを検索し、キーワードとの一致度でスコアリングして並び替える関数
    """
    request_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    params = {'applicationId': app_id, 'format': 'json'}
    if category_id != "0":
        params['categoryId'] = category_id
    
    # キーワードの最初の単語をAPI検索のきっかけに使う（広めに候補を取得するため）
    keywords = keywords_string.split()
    if keywords:
        params['keyword'] = keywords[0]

    response = requests.get(request_url, params=params)
    data = response.json()
    recipes_from_api = data.get('result', [])
    
    # キーワードが入力されている場合のみ、スコアリングと並び替えを行う
    if keywords:
        scored_recipes = []
        for recipe in recipes_from_api:
            score = 0
            title = recipe.get('recipeTitle', '')
            materials = " ".join(recipe.get('recipeMaterial', []))
            search_target = title + materials
            
            # 各キーワードがターゲットに含まれていたらスコアを加算
            for kw in keywords:
                if kw in search_target:
                    score += 1
            
            # 1点でもスコアがあれば候補リストに追加
            if score > 0:
                scored_recipes.append({'recipe': recipe, 'score': score})
        
        # スコアの高い順に並び替え
        sorted_by_score = sorted(scored_recipes, key=lambda x: x['score'], reverse=True)
        # 並び替えたレシピ情報だけをリストとして返す
        return [item['recipe'] for item in sorted_by_score]
    else:
        # キーワードがなければ、APIの結果をそのまま返す
        return recipes_from_api

# --- Streamlitの画面設定 ---
st.title('🍳 今日の献立、何にする？')
APPLICATION_ID = '1076379325522336288'

# --- UI部分 ---
selected_genre = st.selectbox("大まかなジャンルを選んでください", list(RECIPE_CATEGORIES.keys()))
sub_categories = RECIPE_CATEGORIES[selected_genre]
selected_sub_category_name = st.selectbox("具体的な種類を選んでください", list(sub_categories.keys()))
search_keyword = st.text_input('使いたい食材を入力してください（空欄でもOK）')

if st.button('レシピを検索！'):
    category_id_to_search = sub_categories[selected_sub_category_name]
    recipes = search_and_score_recipes(APPLICATION_ID, category_id_to_search, search_keyword)
    
    if recipes:
        st.success("関連性の高い順にレシピを表示します！")
        for recipe in recipes[:10]:
            st.subheader(recipe.get('recipeTitle', '情報なし'))
            st.write(f"**調理時間:** {recipe.get('cookingTime', '情報なし')}")
            st.write(f"**説明:** {recipe.get('recipeDescription', '')}")
            st.write(f"🔗 [レシピを見る]({recipe.get('recipeUrl', '情報なし')})")
            st.markdown("---")
    else:
        st.warning("その条件に合うレシピは見つかりませんでした。")
