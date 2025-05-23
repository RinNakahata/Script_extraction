import streamlit as st
from main_logic import authorize, get_user_list, run_script

st.set_page_config(page_title="台本自動出力アプリ", page_icon="🎬")

st.title("🎬 台本自動出力アプリ")
st.write("以下から自分の名前を選び、出力を開始してください")

client = authorize()
sheet = client.open_by_key(
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx").worksheet("進捗状況")
user_list = get_user_list(sheet)

user_name = st.selectbox("🧑 担当者名を選択", user_list)

if st.button("🚀 出力を開始する"):
    with st.spinner("実行中..."):
        result = run_script(user_name)
        st.success(result)
