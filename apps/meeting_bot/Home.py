import streamlit as st
from meeting_bot.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH

st.set_page_config(page_title="Home", layout = "centered", page_icon=FAVICON_FILE_PATH)

st.logo(LOGO_FILE_PATH)

print(LOGO_FILE_PATH)

st.title("The Modulr Meeting Way")

with st.chat_message("assistant"):
    st.markdown(
        "Hi! I'm **Meeting Bot**. Here to help you have **positive, productive meetings** and follow the **Modulr Meeting Way!**"
    )
    st.markdown("How can I help you with your meeting?")

    st.page_link(
        page="pages/01_The_Modulr_Meeting_Way.py",
        label="What is the Modulr Meeting Way?",
        icon=":material/info:",
    )

    st.page_link(
        page="pages/02_Create_an_agenda.py",
        label="Create an agenda for an upcoming meeting",
        icon=":material/inventory:",
    )

    st.page_link(
        page="pages/03_Summarise_a_meeting.py",
        label="Summarise a previous meeting",
        icon=":material/summarize:",
    )
