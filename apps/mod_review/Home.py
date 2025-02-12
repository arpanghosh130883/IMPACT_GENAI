import streamlit as st
from mod_review.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_review.common.home_constants import overview_markdown

# Initialize session state if needed
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

st.set_page_config(page_title="Overview", layout="centered", page_icon=FAVICON_FILE_PATH)

# Display overview content
st.markdown(overview_markdown)
