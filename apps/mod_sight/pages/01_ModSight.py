import streamlit as st
import json
import time
from decimal import Decimal

from common_app_files.openai import get_openai_response, get_app_name

from common_app_files.code_interpreter_utils import (
    init_session_state,
    upload_dataframe,
    display_message_content,
    handle_assistant_response,
    delete_uploaded_files
)
from common_app_files.openai_code_interpreter import (
    create_assistant,
    create_thread,
    add_files_to_thread,
    add_message_to_thread,
    fetch_all_files,
)

from mod_sight.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_sight.common.constants import APP_NAME, FOOTER_HTML 
from mod_sight.common.code_interpreter_constants import DEFAULT_SYSTEM_PROMPT
from common_app_files.snowflake import get_snowflake_session

from datetime import datetime
from dateutil.relativedelta import relativedelta
from snowflake.snowpark.functions import col, array_agg, lit
from mod_sight.common.modSight_constants import CLIENT_SUMMARY_PROMPT, INSIGHT_SUMMARY_PROMPT, COLUMN_DESC, CI_PROMPT

# Set page config (First Streamlit call)
st.set_page_config(page_title="Code Interpreter", layout="centered", page_icon=FAVICON_FILE_PATH)

# Default Prompts
DEFAULT_CI_PROMPT = CI_PROMPT
DEFAULT_CLIENT_SUMMARY_PROMPT = CLIENT_SUMMARY_PROMPT
DEFAULT_INSIGHT_SUMMARY_PROMPT = INSIGHT_SUMMARY_PROMPT

def get_prompt(SESSION_VAR, PROMPT):
    return st.session_state.get(SESSION_VAR, PROMPT)

def set_prompt(SESSION_VAR, PROMPT):
    st.session_state[SESSION_VAR] = PROMPT

# System prompt editor dialog
@st.experimental_dialog("Modify Prompts", width="large")
def modify_prompts():
    updated_client_summary_prompt = st.text_area(
        label="Edit the client summary prompt",
        value=get_prompt("modified_client_summary_prompt", CLIENT_SUMMARY_PROMPT),
        height=100,
    )    
    updated_insight_summary_prompt = st.text_area(
        label="Edit the insight summary prompt",
        value=get_prompt("modified_insight_summary_prompt", INSIGHT_SUMMARY_PROMPT),
        height=200,
    )
    updated_system_prompt = st.text_area(
        label="Edit the code interpreter prompt",
        value=get_prompt("modified_ci_prompt", CI_PROMPT),
        height=300,
    )    

    # Update buttons for prompts
    if st.button("Update Prompts", disabled=updated_client_summary_prompt is None or updated_insight_summary_prompt is None or updated_system_prompt is None):
        set_prompt("modified_client_summary_prompt", updated_client_summary_prompt)
        set_prompt("modified_insight_summary_prompt", updated_insight_summary_prompt)
        set_prompt("modified_ci_prompt", updated_system_prompt)
        st.info("Prompts updated!")
        time.sleep(1)
        st.rerun()

    if st.button(":red[Reset to default]"):
        set_prompt("modified_client_summary_prompt", DEFAULT_CLIENT_SUMMARY_PROMPT)
        set_prompt("modified_insight_summary_prompt", DEFAULT_INSIGHT_SUMMARY_PROMPT)
        set_prompt("modified_ci_prompt", DEFAULT_CI_PROMPT)
        st.info("Prompts reset to default!")
        time.sleep(1)
        st.rerun()    

# Sidebar for System Prompt and Client Summary Prompt Editor
with st.sidebar:
    if st.button(
        label="Modify Prompts",
        help="Modify both the system prompt and the client summary prompt",
    ):
        modify_prompts()

    if st.button(
        label="Reset",
        help="This will clear the chat history and delete any uploaded files",
    ):
        set_prompt("modified_client_summary_prompt", DEFAULT_CLIENT_SUMMARY_PROMPT)
        set_prompt("modified_insight_summary_prompt", DEFAULT_INSIGHT_SUMMARY_PROMPT)
        set_prompt("modified_ci_prompt", DEFAULT_CI_PROMPT)
        st.rerun()

# Initialize App
def init_app():
    get_app_name(APP_NAME)
    st.logo(LOGO_FILE_PATH)
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# Initialize Session State
def init_session_variables():
    if "selected_partner" not in st.session_state:
        st.session_state.selected_partner = None
    if "openai_client_summary_response" not in st.session_state:
        st.session_state.openai_client_summary_response = ""
    if "openai_partner_insight_response" not in st.session_state:
        st.session_state.openai_partner_insight_response = ""
    init_session_state()

@st.experimental_dialog("Raw Data", width="large")
def show_raw_data(selected_partner, raw_data):
    with st.expander("Data for " + selected_partner):
        st.dataframe(raw_data)

def create_client_summary_df(session):
    dim_modulr_client = session.table('CORE.DWH.DIM_MODULR_CLIENT').filter(col("UNIQUE_CLIENT_NAME").is_not_null())
    fct_monthly_client_summary = session.table('CORE.DWH.FCT_MONTHLY_CLIENT_SUMMARY').filter(col("dim_modulr_client_key") != 0)
    
    df = (
        fct_monthly_client_summary
        .join(dim_modulr_client, dim_modulr_client.dim_modulr_client_key == fct_monthly_client_summary.dim_modulr_client_key)
        .select(
            fct_monthly_client_summary.client_salesforce_id.alias('SALESFORCE_ID'),
            fct_monthly_client_summary.client_legal_entity.alias('LEGAL_ENTITIES'),
            fct_monthly_client_summary.month_end_date,
            fct_monthly_client_summary.dim_month_key,
            fct_monthly_client_summary.dim_modulr_client_key.alias('DIM_CLIENT_KEY'),
            fct_monthly_client_summary.clean_transaction_revenue_gbp,
            fct_monthly_client_summary.budget_revenue_gbp,
            fct_monthly_client_summary.forecast_method,
            fct_monthly_client_summary.forecast_revenue_gbp,
            fct_monthly_client_summary.future_forecast_revenue_gbp,
            fct_monthly_client_summary.clean_minimum_top_up_gbp,
            fct_monthly_client_summary.contracted_minimum_gbp,
            fct_monthly_client_summary.number_of_open_accounts,
            fct_monthly_client_summary.number_of_new_accounts,
            fct_monthly_client_summary.number_of_transacting_accounts,
            fct_monthly_client_summary.inbound_app_fraud_volume,
            fct_monthly_client_summary.inbound_app_fraud_value_gbp,
            fct_monthly_client_summary.number_of_customers,
            fct_monthly_client_summary.number_of_new_customers,
            fct_monthly_client_summary.number_of_transacting_customers,
            fct_monthly_client_summary.transaction_volume,
            fct_monthly_client_summary.transaction_value_gbp,
            fct_monthly_client_summary.average_balance_gbp,
            dim_modulr_client.unique_client_identifier,
            dim_modulr_client.client_name,
            dim_modulr_client.unique_client_name,
            dim_modulr_client.client_signed_cohort_date,
            dim_modulr_client.revenue_cohort_month_end_date,
            dim_modulr_client.client_contracted_entity,
            dim_modulr_client.client_account_type,
            dim_modulr_client.client_status,
            dim_modulr_client.client_vertical,
            dim_modulr_client.client_sub_vertical,
            dim_modulr_client.client_rag_status,
            dim_modulr_client.client_tier,
            dim_modulr_client.client_billing_street,
            dim_modulr_client.client_billing_city,
            dim_modulr_client.client_billing_country,
            dim_modulr_client.client_billing_postcode,
            dim_modulr_client.client_description,
            dim_modulr_client.client_currency,
            dim_modulr_client.client_annual_revenue,
            dim_modulr_client.client_total_sme_count,
            dim_modulr_client.client_total_sme_reached,
            dim_modulr_client.client_current_amount,
            dim_modulr_client.client_overdue_amount_30_days,
            dim_modulr_client.client_overdue_amount_31_to_60_days,
            dim_modulr_client.client_overdue_amount_61_to_90_days,
            dim_modulr_client.client_overdue_amount_over_90_days,
            dim_modulr_client.client_renewal_date,
            dim_modulr_client.parent_client_name,
            dim_modulr_client.parent_client_signed_cohort_date,
            dim_modulr_client.parent_client_contracted_entity,
            dim_modulr_client.parent_client_account_type,
            dim_modulr_client.parent_client_status,
            dim_modulr_client.parent_client_vertical,
            dim_modulr_client.parent_client_sub_vertical,
            dim_modulr_client.parent_client_rag_status,
            dim_modulr_client.parent_client_tier,
            dim_modulr_client.parent_client_billing_street,
            dim_modulr_client.parent_client_billing_city,
            dim_modulr_client.parent_client_billing_country,
            dim_modulr_client.parent_client_billing_postcode,
            dim_modulr_client.parent_client_description,
            dim_modulr_client.parent_client_currency,
            dim_modulr_client.parent_client_annual_revenue,
            dim_modulr_client.parent_client_total_sme_count,
            dim_modulr_client.parent_client_total_sme_reached,
            dim_modulr_client.parent_client_renewal_date,
            fct_monthly_client_summary.dwh_created_at,
            fct_monthly_client_summary.dwh_updated_at
        )
        .order_by(dim_modulr_client.UNIQUE_CLIENT_NAME)
    )
    return df

def partner_monthly_summary_df(client_summary_df):
    df = (client_summary_df      
        .select(
            'MONTH_END_DATE',
            'NUMBER_OF_OPEN_ACCOUNTS',
            'NUMBER_OF_NEW_ACCOUNTS',
            'NUMBER_OF_TRANSACTING_ACCOUNTS',
            'NUMBER_OF_CUSTOMERS',
            'NUMBER_OF_NEW_CUSTOMERS',
            'NUMBER_OF_TRANSACTING_CUSTOMERS',    
            'INBOUND_APP_FRAUD_VOLUME',
            'INBOUND_APP_FRAUD_VALUE_GBP',
            'CLEAN_TRANSACTION_REVENUE_GBP',
            'FORECAST_REVENUE_GBP', 
            'CLEAN_MINIMUM_TOP_UP_GBP',
            'TRANSACTION_VOLUME',
            'TRANSACTION_VALUE_GBP',
            'CLIENT_OVERDUE_AMOUNT_30_DAYS',
        )
        .filter(col('UNIQUE_CLIENT_NAME') == lit(st.session_state.selected_partner))
        .filter(col('MONTH_END_DATE') >= (datetime.today() - relativedelta(years=2)).date())
        .filter(col('MONTH_END_DATE') <= datetime.today())
        .sort(col('MONTH_END_DATE').asc())
    )
    return df

def generate_prompt_insight(partner_monthly_summary):    
    nl_transactions = []  
    prev_tr = 0
    for row in partner_monthly_summary.collect():
        if prev_tr == 0.00 and row['CLEAN_TRANSACTION_REVENUE_GBP'] == 0.00:
            nl_transactions.append('clean revenue had no change in revenue from the previous month in ' + row['MONTH_END_DATE'].strftime("%B %Y"))
        else:
            percent_change = get_change(row['CLEAN_TRANSACTION_REVENUE_GBP'], prev_tr)
            nl_transactions.append('clean revenue had ' + str(percent_change) + ' percent of revenue from the previous month in ' + row['MONTH_END_DATE'].strftime("%B %Y"))
        prev_tr = row['CLEAN_TRANSACTION_REVENUE_GBP']
    
    prompt_insight = (
        'The meaning of the columns is as follows:' +
        ', '.join(COLUMN_DESC) +
        '\n\nHere is some breakdowns of the transaction data:' +
        ', '.join(nl_transactions) +
        '\nTotal revenue year to date is ' + 
        str(partner_monthly_summary.agg(("CLEAN_TRANSACTION_REVENUE_GBP", "sum")).to_pandas().iloc[0][0]) +
        f'\n{INSIGHT_SUMMARY_PROMPT}'
    )
    return prompt_insight

def create_partner_desc(partner):
    flags = {'MFBV': ':flag-eu:', 'MFSL': ':flag-gb:'}
    partner_flags = [flags[legal_entity] for legal_entity in json.loads(partner['LEGAL_ENTITIES'])]

    partner_desc = (
        f"{partner['UNIQUE_CLIENT_NAME']} ({', '.join(partner_flags)})" +
        f" is a {partner['CLIENT_VERTICAL']} for {partner['CLIENT_SUB_VERTICAL']}" +
        f" and has a {partner['CLIENT_ACCOUNT_TYPE']} account type. " +
        f"It is currently {partner['CLIENT_STATUS']}." +
        f"\nThey signed on: {partner['CLIENT_SIGNED_COHORT_DATE']}"
    )
    return partner_desc

def get_change(current, previous):
    # Handle None values by treating them as zero
    current = Decimal(current or '0')
    previous = Decimal(previous or '0')

    try:
        if current == 0 and previous == 0:
            return Decimal('0.00')  # No change if both are zero
        percentage = abs(previous - current) / max(previous, current) * 100
        return round(percentage, 2)
    except ZeroDivisionError:
        return Decimal('inf')

# Main Function
def main():
    init_app()
    init_session_variables()

    session = get_snowflake_session()
    client_summary_df = create_client_summary_df(session)
    partners_df = (
        client_summary_df
        .group_by(
            col('UNIQUE_CLIENT_NAME'),
            col('CLIENT_SIGNED_COHORT_DATE'),
            col('REVENUE_COHORT_MONTH_END_DATE'),
            col('CLIENT_ACCOUNT_TYPE'),
            col('CLIENT_STATUS'),
            col('CLIENT_VERTICAL'),
            col('CLIENT_SUB_VERTICAL'),
            col('CLIENT_RAG_STATUS'),
            col('CLIENT_TIER'),
            col('CLIENT_DESCRIPTION'),
            col('CLIENT_RENEWAL_DATE')
        )
        .agg(array_agg(col('LEGAL_ENTITIES'), is_distinct=True).alias('LEGAL_ENTITIES'))
        .order_by('UNIQUE_CLIENT_NAME')
    )

    # Create dropdown and update session state
    selected_partner = st.selectbox("Select Client", 
                                    partners_df,
                                    index=None,
                                    placeholder="Please select a client",)

    if selected_partner != st.session_state.selected_partner:
        # Clear session state and cache data
        st.session_state.clear()
        st.cache_data.clear()

        # Initialize session state
        init_session_variables()

        # Reset session history
        st.session_state.selected_partner = selected_partner

        partner_monthly_summary = partner_monthly_summary_df(client_summary_df)        

        # Delete existing files before uploading a new one
        data = fetch_all_files()
        fil_ids = [file_object.id for file_object in data]    
        delete_uploaded_files(fil_ids)

        upload_dataframe(partner_monthly_summary.to_pandas())

        partner = (
            partners_df
            .filter(col('UNIQUE_CLIENT_NAME') == lit(st.session_state.selected_partner))
            .to_pandas()
            .iloc[0]
        )
        
        partner_desc = create_partner_desc(partner)
        content = partner.to_json(orient='records', lines=True) + '\n' + partner_desc + '\n\n' + CLIENT_SUMMARY_PROMPT
        
        st.session_state.openai_client_summary_response = get_openai_response(messages=[{"role": "user", "content": content}])    
        st.session_state.partner_monthly_summary = partner_monthly_summary_df(client_summary_df)        

        if partner_monthly_summary.filter(col('CLEAN_TRANSACTION_REVENUE_GBP') != 0).count() == 0:
            st.write('Partner has not made any transactions in the past 2 years.')
        else:
            prompt_insight = generate_prompt_insight(partner_monthly_summary)
            st.session_state.openai_partner_insight_response = get_openai_response(messages=[{"role": "user", "content": prompt_insight}])    

        st.rerun()

    if st.session_state.selected_partner and st.session_state.openai_client_summary_response and st.session_state.openai_partner_insight_response:

        st.write(st.session_state.openai_client_summary_response)
        st.divider()

        with st.sidebar:
            if st.button("Show Raw Data"):
                show_raw_data(st.session_state.selected_partner, st.session_state.partner_monthly_summary)
        
        st.write(st.session_state.openai_partner_insight_response)
        st.divider()
        
        if "assistant_id" not in st.session_state:
            st.session_state["assistant_id"] = None
            assistant = create_assistant(DEFAULT_SYSTEM_PROMPT)
            st.session_state.assistant_id = assistant.id
        
        if st.session_state.thread_id is None:
            thread = create_thread()
            st.session_state.thread_id = thread.id

        messages = 'messages'
        if messages not in st.session_state:
            st.session_state[messages] = []
            
        add_files_to_thread(st.session_state.thread_id, st.session_state.file_id)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                display_message_content(message["items"])

        if st.session_state.messages == []:
            add_message_to_thread(st.session_state.thread_id, CI_PROMPT)
            with st.chat_message("assistant"):
                handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)

    if prompt := st.chat_input("Ask me a question about your dataset"):
        st.session_state.messages.append({"role": "user", "items": [{"type": "text", "content": prompt}]})
        add_message_to_thread(st.session_state.thread_id, prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)

if __name__ == "__main__":
    main()
