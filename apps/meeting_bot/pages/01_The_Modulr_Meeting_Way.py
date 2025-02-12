import streamlit as st
from meeting_bot.common.media_path import LOGO_FILE_PATH, RECORD_AND_TRANSCRIBE, FAVICON_FILE_PATH
from meeting_bot.common.modulr_meeting_way_constants import overview_markdown, user_guide_markdown_1, user_guide_markdown_2

st.logo(LOGO_FILE_PATH)

st.set_page_config(page_title="The Modulr Meeting Way", layout = "centered", page_icon=FAVICON_FILE_PATH)

# st.title("Modulr Meeting Way")

tab1, tab2 = st.tabs(["Overview", "User Guide"])

with tab1:
    st.markdown(overview_markdown)

with tab2:
    st.markdown(user_guide_markdown_1)
    st.image(RECORD_AND_TRANSCRIBE)
    st.markdown(user_guide_markdown_2)