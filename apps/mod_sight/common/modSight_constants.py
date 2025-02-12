#import altair_saver
#import altair as alt
from mod_sight.common.code_constants import ACCOUNTS_ANALYSIS_CODE, TRANSACTION_REVENUE_CODE, CUSTOMER_ANALYSIS_CODE, REVENUE_FORECAST_CODE,FRAUD_ANALYSIS_CODE

CLIENT_SUMMARY_PROMPT = """Put a heading **Client Summary:** Respond with markdown, and only return the bullet points. Provide a summary of the client with the following details and a short client summary on where it is based, services it offers, and the business area they target:

- **Client Name**: [Insert UNIQUE_CLIENT_NAME]
- **Country**: [Country Name]
- **Industry**: [Industry]
- **Sector**: [Sector]
- **Account Type**: [Account Type]
- **Account Status**: [Account Status]
- **Sign-up Date**: [Sign-up Date]
- **Program Type**: [Program Type]
- **Marketing Message**: [Marketing Message]
- **Associated Entities**: [LEGAL_ENTITIES, if any]

[Client Name] is based in [Country], specializing in [Industry/Services]. They focus on providing [specific services or solutions] targeting [business area or sector].
"""


INSIGHT_SUMMARY_PROMPT ="""Please summarise transaction trends based on MONTH_END_DATE, only using highlights in the data.' +
'Respond with markdown, and only return the bullet points with no commentary. Highlight in bold any important points' +
'Do not include any raw data for the month, and convert raw dates into the month. Put a heading **Transaction Summary:**. Use 5 bulletpoints."""

CI_PROMPT = f"""Analyze the provided data and generate insightful visualizations and data analysis for the following categories:

1. **Accounts Analysis**: Plot the number of open, new and transacting accounts over time using this code: {ACCOUNTS_ANALYSIS_CODE}.
2. **Transactions & Revenue**: Plot transaction volume and transaction value over time, using this code: {TRANSACTION_REVENUE_CODE}.
3. **Customer Analysis**: Plot the number of customers, new customers, and transacting customers over time, using this code: {CUSTOMER_ANALYSIS_CODE}.
4. **Fraud Analysis**: Plot the inbound application fraud volume and value over time, using this code: {FRAUD_ANALYSIS_CODE}.
5. **Revenue & Forecast**: Plot clean transaction revenue, clean minimum top-up, and forecast revenue over time using this code: {REVENUE_FORECAST_CODE} (if forecast data is available).

Task: After displaying the visuals, provide an in-depth data analysis for each chart, focusing on meaningful insights rather than just describing the colors and aesthetics. The prompt should guide the interpretation of the data trends, patterns, and relationships based on the plot visuals.

Note: Do not mention or describe the cleaning process.
"""

COLUMN_DESC = [
    'MONTH_END_DATE: The end date of the month',
    'NUMBER_OF_OPEN_ACCOUNTS: Number of open accounts',
    'NUMBER_OF_NEW_ACCOUNTS: Number of new accounts',
    'NUMBER_OF_TRANSACTING_ACCOUNTS: Number of transacting accounts',
    'NUMBER_OF_CUSTOMERS: Number of customers',
    'NUMBER_OF_NEW_CUSTOMERS: Number of new customers',
    'NUMBER_OF_TRANSACTING_CUSTOMERS: Number of transacting customers',
    'CLEAN_TRANSACTION_REVENUE_GBP: Quality cleaned raw TR by a human',
    'FORECAST_REVENUE_GBP: Refreshed revenue target generally performance every QTR',
    'CLEAN_MINIMUM_TOP_UP_GBP: Total clean minimum top up in GBP. If clients transaction volume is less than their contracted minimums, this is the difference between their actual transaction revenue and the minimums they pay.',
    'INBOUND_APP_FRAUD_VALUE_GBP: Defined as fraud by fraud team.  Inbound TX Value only.',
    'TRANSACTION_VOLUME: No of transactions',
    'TRANSACTION_VALUE_GBP: Value of transactions',
    'CLIENT_OVERDUE_AMOUNT_30_DAYS: Outstanding billed amount at 30 days'
]