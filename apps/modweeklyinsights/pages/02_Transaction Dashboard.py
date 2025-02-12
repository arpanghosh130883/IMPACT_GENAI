from fpdf import FPDF
import plotly.express as px
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from common_app_files.openai import get_openai_response, get_app_name
from modweeklyinsights.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from modweeklyinsights.common.html_constants import APP_NAME, FOOTER_HTML
from modweeklyinsights.common.mod_analytics_constants_trans import CI_PROMPT
from common_app_files.snowflake import get_snowflake_session

# Set page config
st.set_page_config(page_title="Code Interpreter", layout="centered", page_icon=FAVICON_FILE_PATH)

# Initialize the app
def init_app():
    get_app_name(APP_NAME)
    st.logo(LOGO_FILE_PATH)
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# Generate narrative using OpenAI and CI_PROMPT
def generate_narrative(data, start_date, end_date):
    # Group and prepare metrics data for the prompt
    industry_group = data.groupby('INDUSTRY').agg({
        'TXN_VOLUME': 'sum',
        'TXN_VALUE': 'sum',
        #'CLIENT_NAME': 'count'  # Total number of transactions
    }).reset_index()

    client_group = data.groupby('CLIENT_NAME').agg({
        'TXN_VOLUME': 'sum',
        'TXN_VALUE': 'sum',
        'ANNUAL_REVENUE': 'max',
        'TRANSACTION_DATE': lambda x: ", ".join(x.dt.strftime('%d-%m-%Y').unique())
    }).reset_index()

    payment_group = data.groupby('PAYMENT_SCHEME').agg({
        'TXN_VOLUME': 'sum',
        'TXN_VALUE': 'sum'
    }).reset_index()

    # Extract details for the top metrics
    top_industries = industry_group.sort_values(by='TXN_VALUE', ascending=False).head(5).to_dict(orient='records')
    top_clients = client_group.sort_values(by='TXN_VALUE', ascending=False).head(5).to_dict(orient='records')
    top_schemes = payment_group.sort_values(by='TXN_VALUE', ascending=False).head(5).to_dict(orient='records')

    # Create the formatted data for CI_PROMPT
    prompt_content = CI_PROMPT.format(
        START_DATE=start_date.strftime('%d-%m-%Y'),
        END_DATE=end_date.strftime('%d-%m-%Y'),
        TOP_INDUSTRIES=top_industries,
        TOP_CLIENTS=top_clients,
        TOP_SCHEMES=top_schemes
    )

    # Create the message structure for OpenAI response
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that provides detailed summaries based on commercial and operational metrics."
        },
        {
            "role": "user",
            "content": prompt_content
        }
    ]

    # Generate the narrative using OpenAI
    try:
        response = get_openai_response(messages)
    except Exception as e:
        response = f"Error generating narrative: {str(e)}"
    
    return response

# Data Filtering Function
def filter_data(data, start_date, end_date, TYPE=None, Client_status=None, Transaction=None, Legal_Entity=None):
    filtered_data = data[(data["TRANSACTION_DATE"] >= start_date) & (data["TRANSACTION_DATE"] <= end_date)]
    
    if TYPE:
        filtered_data = filtered_data[filtered_data['CLIENT_TYPE'] == TYPE]
    if Client_status:
        filtered_data = filtered_data[filtered_data['SALESFORCE_STATUS'] == Client_status]
    if Transaction:
        filtered_data = filtered_data[filtered_data['TRANSACTION_DIRECTION'] == Transaction]
    if Legal_Entity:
        filtered_data = filtered_data[filtered_data['CLIENT_LEGAL_ENTITY'] == Legal_Entity]
    
    return filtered_data

# Export to PDF Function
def export_to_pdf(narrative):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, narrative)
    pdf_file = "executive_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Main App
def main():
    init_app()

    # Load and preprocess data
    session = get_snowflake_session()

    data = (
        session.table('IMPACT_GENAI.MODWEEKLYINSIGHTS.EXEC_SCORECARD_LATEST_DATA')
    )

    data = data.to_pandas()
    
    data['TRANSACTION_DATE'] = pd.to_datetime(data['TRANSACTION_DATE'], format='%d-%m-%Y', errors='coerce')
    data = data.dropna(subset=['TRANSACTION_DATE'])

    # Sidebar filters
    start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=6))
    end_date = st.sidebar.date_input("End Date", datetime.today())
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    TYPE = st.sidebar.selectbox("Type", options=[None] + data["CLIENT_TYPE"].dropna().unique().tolist())
    Client_status = st.sidebar.selectbox("Client Status", options=[None] + data["SALESFORCE_STATUS"].dropna().unique().tolist())
    Transaction = st.sidebar.selectbox("Transaction", options=[None] + data["TRANSACTION_DIRECTION"].dropna().unique().tolist())
    Legal_Entity = st.sidebar.selectbox("Legal Entity", options=[None] + data["CLIENT_LEGAL_ENTITY"].dropna().unique().tolist())

    # Filter data based on the selected period and filters
    filtered_data = filter_data(data, start_date, end_date, TYPE, Client_status, Transaction, Legal_Entity)

    # Generate narrative based on the filtered data using OpenAI
    st.title("Transaction Dashboard - Weekly Report")
    combined_narrative = generate_narrative(filtered_data, start_date, end_date)
    st.markdown(combined_narrative, unsafe_allow_html=True)

    # Export to PDF
    if st.sidebar.button("Export to PDF"):
        pdf_file = export_to_pdf(combined_narrative)
        with open(pdf_file, "rb") as f:
            st.sidebar.download_button(label="Download PDF", data=f, file_name="executive_report.pdf")

if __name__ == "__main__":
    main()
