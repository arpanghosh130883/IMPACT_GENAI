from fpdf import FPDF
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from common_app_files.openai import get_openai_response, get_app_name
from modweeklyinsights.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from modweeklyinsights.common.html_constants import APP_NAME, FOOTER_HTML
from modweeklyinsights.common.mod_analytics_constants_deals import CI_PROMPT
from common_app_files.snowflake import get_snowflake_session

# Set page config
st.set_page_config(page_title="Code Interpreter", layout="centered", page_icon=FAVICON_FILE_PATH)

# Initialize the app
def init_app():
    get_app_name(APP_NAME)
    st.logo(LOGO_FILE_PATH)
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# Generate narrative using OpenAI and CI_PROMPT
def generate_narrative(deals_narrative, new_clients_narrative, start_date, end_date):
    # Create the formatted data for CI_PROMPT
    prompt_content = CI_PROMPT.format(
        START_DATE=start_date.strftime('%d-%m-%Y'),
        END_DATE=end_date.strftime('%d-%m-%Y'),
        DEALS_NARRATIVE=deals_narrative,
        NEW_CLIENTS_NARRATIVE=new_clients_narrative
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

# Prepare deals signed narrative
def prepare_deals_signed(deals_data):
    deals_data["DEAL_VALUE"] = pd.to_numeric(deals_data["DEAL_VALUE"], errors="coerce")
    if not deals_data.empty:
        deals_summary = []
        for client, group in deals_data.groupby("CLIENT_NAME"):
            unique_deal_entries = group[["DEAL_VALUE", "CLIENT_LEGAL_ENTITY"]].drop_duplicates()
            formatted_deal_values = ", ".join(
                f"£{row['DEAL_VALUE']:,.2f} (Legal Entity: {row['CLIENT_LEGAL_ENTITY']})"
                for _, row in unique_deal_entries.iterrows() if pd.notnull(row["DEAL_VALUE"])
            )
            # Extract unique deal values for each client and sum them
            #unique_deal_values = group["DEAL_VALUE"].unique()
            #deal_value = unique_deal_values.sum()
            #formatted_deal_values = ", ".join(f"£{val:,.2f}" for val in unique_deal_values)
            #deal_value = group["DEAL_VALUE"].sum() # DEAL_VALUE added on 29-10-2024
            industry = group["INDUSTRY"].iloc[0]
            signed_date = group["LATEST_DEAL_CLOSE_DATE"].max().strftime('%d-%m-%Y')
            deals_summary.append(f"Client: **{client}**, Deal Value: **£{formatted_deal_values}**, Vertical: **{industry}**, Signed Date: **{signed_date}**")
        return "\n".join(deals_summary)
    else:
        return "No deals signed during the selected period."

# Prepare new clients onboarded narrative
def prepare_new_clients_onboarded(new_clients_data, start_date, end_date):
    # Filter new clients based on the 'SALESFORCE_STATUS' being 'Live' and 'LATEST_DEAL_CLOSE_DATE' within the selected period
    filtered_new_clients = new_clients_data[
        (new_clients_data['SALESFORCE_STATUS'] == 'Live') &
        (new_clients_data['LATEST_DEAL_CLOSE_DATE'].between(start_date, end_date))
    ]

    if not filtered_new_clients.empty:
        new_clients_count = filtered_new_clients["CLIENT_NAME"].nunique()
        new_clients_details = filtered_new_clients.groupby("CLIENT_NAME").first().apply(
            lambda row: f"{row.name} ({row['INDUSTRY']})", axis=1).tolist()
        return f"**{new_clients_count}** New Clients Onboarded / Client Renewal this week: " + ", ".join(new_clients_details)
    else:
        return "No new clients onboarded / Client Renewal during the selected period."

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

    session = get_snowflake_session()

    data = (
        session.table('IMPACT_GENAI.MODWEEKLYINSIGHTS.EXEC_SCORECARD_LATEST_DATA')
    )

    data = data.to_pandas()
    
    # Load and preprocess data
    # data = pd.read_csv('/home/arpan_ghosh/impact-genai/apps/modweeklyinsights/data/EXEC_SCORECARD_LATEST_DATA_OCT24.csv', encoding='ISO-8859-1')

    data['TRANSACTION_DATE'] = pd.to_datetime(data['TRANSACTION_DATE'], format='%d-%m-%Y', errors='coerce')
    #data = data.dropna(subset=['TRANSACTION_DATE'])
    data['LATEST_DEAL_CLOSE_DATE'] = pd.to_datetime(data['LATEST_DEAL_CLOSE_DATE'], format='%d-%m-%Y', errors='coerce')
    #data = data.dropna(subset=['LATEST_DEAL_CLOSE_DATE'])

     # Drop rows with invalid date conversions
    data = data.dropna(subset=['TRANSACTION_DATE', 'LATEST_DEAL_CLOSE_DATE'])


    # Sidebar filters
    start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=6))
    end_date = st.sidebar.date_input("End Date", datetime.today())
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Sidebar filters for additional customization (if needed)
    TYPE = st.sidebar.selectbox("Type", options=[None] + data["CLIENT_TYPE"].dropna().unique().tolist())
    Client_status = st.sidebar.selectbox("Client Status", options=[None] + data["SALESFORCE_STATUS"].dropna().unique().tolist())
    Transaction = st.sidebar.selectbox("Transaction", options=[None] + data["TRANSACTION_DIRECTION"].dropna().unique().tolist())
    Legal_Entity = st.sidebar.selectbox("Legal Entity", options=[None] + data["CLIENT_LEGAL_ENTITY"].dropna().unique().tolist())

    # Filter data based on the selected period and filters
    filtered_data = filter_data(data, start_date, end_date, TYPE, Client_status, Transaction, Legal_Entity)

    # Analyze data for deals signed and new clients onboarded
    deals_signed = filtered_data[filtered_data["LATEST_DEAL_CLOSE_DATE"].between(start_date, end_date)]
    new_clients_onboarded = deals_signed[deals_signed["SALESFORCE_STATUS"] == "Live"]

    # Prepare narratives
    deals_narrative = prepare_deals_signed(deals_signed)
    new_clients_narrative = prepare_new_clients_onboarded(new_clients_onboarded,start_date, end_date)

    # Generate combined narrative using OpenAI
    combined_narrative = generate_narrative(deals_narrative, new_clients_narrative, start_date, end_date)

    # Display the narrative
    st.title("Executive Dashboard - Weekly Report")
    st.markdown(combined_narrative, unsafe_allow_html=True)

    # Export to PDF
    if st.sidebar.button("Export to PDF"):
        pdf_file = export_to_pdf(combined_narrative)
        with open(pdf_file, "rb") as f:
            st.sidebar.download_button(label="Download PDF", data=f, file_name="executive_report.pdf")

if __name__ == "__main__":
    main()
