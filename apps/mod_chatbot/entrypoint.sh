#!/bin/bash
python3 -m streamlit run /app/mod_chatbot/Home.py --server.address=0.0.0.0 $@ 2>&1