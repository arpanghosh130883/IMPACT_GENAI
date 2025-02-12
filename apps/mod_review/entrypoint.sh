#!/bin/bash
python3 -m streamlit run /app/mod_review/Home.py --server.address=0.0.0.0 --server.maxUploadSize=100 $@ 2>&1
