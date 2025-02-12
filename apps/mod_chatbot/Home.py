import streamlit as st
from mod_chatbot.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH

st.set_page_config(page_title="Home", layout = "centered", page_icon=FAVICON_FILE_PATH)

st.logo(LOGO_FILE_PATH)

print(LOGO_FILE_PATH)

st.title("Welcome to ModBot2.0🤖")

with st.chat_message("assistant"):
    st.markdown(
        "Hi! I'm **Chat Bot**, your intelligent assistant. I'm here to help you by answering your questions and analyzing documents for insights.\n\n"
        "**What is it for?**\n"
        "- ModChatBot is designed to assist you with general knowledge queries, document reviews, and providing concise, actionable insights.\n\n"
        "**What is it suitable for?**\n"
        "- Uploading documents like contracts or reports (in PDF or DOCX format) for quick analysis.\n"
        "- Queries that require clear and factual answers or assistance in understanding uploaded documents.\n\n"
        "**Guidance on Using ModChatBot:**\n"
        "- Start by asking any question or uploading a document for review.\n"
        "- Ensure your document is appropriate for AI analysis (e.g., contains low-sensitive or non-critical content).\n"
        "- Interact with me to refine outputs, clarify your queries, or explore deeper insights.\n\n"
        "**Customizing My Behavior:**\n"
        "- You can customize my system prompt to tailor my responses according to your specific needs.\n"
        "- Use the **Modify System Prompt** feature to adjust instructions, refine my tone, or change the way I analyze and respond to queries.\n\n"
        "**Privacy and Safety Notice:**\n"
        "- Please **do not upload any sensitive user demographic data** or personally identifiable information (**PII**).\n"
        "- All interactions are processed with privacy and security in mind, but avoid sharing confidential or proprietary information.\n\n"
    )

    st.markdown("**How can I assist you today?**")

    st.page_link(
        page="pages/01_Chatbot.py",
        label="Explore ChatBot Features",
        icon="💬",
    )

