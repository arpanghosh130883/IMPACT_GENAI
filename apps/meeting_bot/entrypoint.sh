#!/bin/bash
python3 -m streamlit run /app/meeting_bot/Home.py --server.address=0.0.0.0 $@ 2>&1