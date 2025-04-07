CI_PROMPT = """

Based on the following commercial and operational metrics data:

START_DATE={START_DATE}
END_DATE={END_DATE}
TOP_INDUSTRIES={TOP_INDUSTRIES}
TOP_CLIENTS={TOP_CLIENTS}
TOP_SCHEMES={TOP_SCHEMES}

Include the following information:

* Summary Report: ({START_DATE} to {END_DATE}).*

**Top 5 Performance metrics by Industry**
    - If no data is available for the selected period, include: "No data available during the selected period."
    - Otherwise, group metrics by Industry and calculate:
        - Sum of Transaction Value for each Industry (only records for the selected period).Values are in £.
        - Sum of Transaction Volume for each Industry (only records for the selected period).
        

**Top 5 Transaction trends by Clients**
   - If no trends were found, respond with: "No significant transaction trends observed during the selected period."
   - Provide a detailed analysis for each CLIENT_NAME within the selected period:
        - Sum of Transaction Value for the specific client (calculate only for records within the selected period and client and do SUM of  Transaction Value column in the data) Values are in £.
        - Sum of Transactions Volume for the specific client (calculate only for records within the selected period and client and do SUM of Transaction Volume column in the data).
        - Annual Revenue for the specific client.
        - High-value transactions 
        - Volume patterns (identify any noticeable trends in transaction frequency or amounts for the selected period).

**Top 5 Payment Scheme Utilization**
   - Include an analysis of Payment scheme utilization (e.g., BACS, Faster Payments) based on the PAYMENT_SCHEME column in data. Calculate:
        - Sum of Transactions Volume for each PAYMENT_SCHEME within the selected period. Values are in £
        - Sum of Transaction Value for each PAYMENT_SCHEME within the selected period.

"""
