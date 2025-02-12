CI_PROMPT = """

Based on the following commercial and operational metrics data:
Client Name: {CLIENT_NAME}
Transaction Type: {TRANSACTION_TYPE}
Transaction Volume: {TXN_VOLUME}
Transaction Value: {TXN_VALUE}
Client Signed Date: {CLIENT_SIGNED_COHORT_DATE}
Industry: {INDUSTRY}
Annual Revenue: {ANNUAL_REVENUE}
Client Status: {CLIENT_STATUS}

Include the following information:

* Metrics for the selected period ({START_DATE} to {END_DATE}).*

**List of deals signed during the selected period**
    - If no deals were signed in the selected period, include: "No deals signed during the selected period."
    - Otherwise, include client names, deal values, and industries (Client Vertical).
        Example: “Client: ABC Ltd, Deal Value: £500,000, Vertical: Retail, Signed Date: 10/15/2024”

**New clients onboarded during the selected period**
    - If no new clients were onboarded in the selected period, include: "No new clients onboarded during the selected period."
    - Otherwise, summarize Number of new clients onboarded with relevant details such as onboarding date and industry.
        Example: “5 New Clients Onboarded This Week: ABC Ltd (Retail), XYZ Corp (Healthcare), etc.”

**Performance metrics by vertical (industry) during the selected period**
    - If no data is avaiable for the selected period, include: " No data available during the selected period."
    - Otherwise Perform Group of metrics by vertical to show how each industry is performing during selected period

**Financial Performance during the selected period**
    - If no data is avaiable for the selected period, include: " No data available during the selected period."
    - Provide Summary of Financial performance, highlighting revenue growth, changes in transaction volumes, and trends during during selected period

**Transaction trends during the selected period **:
   - If no trends were found, respond with: "No significant transaction trends observed during the selected period."
   - Avoid placeholders like "Client A" or "Client B" unless actual data is available.
   - If CLIENT_NAME is present in the selected period provide analysis of each Client basis its TXN_VOLUME & TXN_VALUE and ANNUAL_REVENUE, high value transactions and volume patterns

**Payment scheme utilization during the selected period **:
   - Include analysis on Payment scheme utilization (e.g., BACS, Faster Payments) based on PAYMENT_SCHEME column in data along with TXN_VOLUME & TXN_VALUE  associated with each of PAYMENT_SCHEME during the selected period

**Cash flow during the selected period **:
   - If no cash flow data is available, respond with: "No cash flow data available for this period."
   - Inlcude TX_VOLUME and TRANSACTION_DIRECTION (Inbound, Outbound) analysis basis each of the Client during the selected period.


"""
