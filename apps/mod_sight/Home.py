import streamlit as st
from mod_sight.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_sight.common.home_constants import overview_markdown

st.set_page_config(page_title="Overview", layout = "centered", page_icon=FAVICON_FILE_PATH)

st.logo(LOGO_FILE_PATH)

# print(LOGO_FILE_PATH)

st.markdown(overview_markdown)