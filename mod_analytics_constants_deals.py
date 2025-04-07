CI_PROMPT = """

Based on the following commercial and operational metrics data:

START_DATE={START_DATE}
END_DATE={END_DATE}
DEALS_NARRATIVE={DEALS_NARRATIVE}
NEW_CLIENTS_NARRATIVE={NEW_CLIENTS_NARRATIVE}


Include the following information:

* Summary Report: ({START_DATE} to {END_DATE}).*

**List of deals signed**
    - If no deals were signed in the selected period, include: "No deals signed during the selected period."
    - Otherwise, include client names, Deal Value for each cleint per each Legal Entiry, and industries (Client Vertical).
        Example: “Client: ABC Ltd, Deal Value: £500,000 (Legal Entity:MFBV) and £300,000 (Legal Entity:MFSL) , Vertical: Retail, Signed Date: 10/15/2024”

**New clients Onboarded / Client Renewal **
    - If no new clients were onboarded in the selected period, include: "No new clients onboarded / No Clients Renewal during the selected period."
    - Otherwise, summarize the Number of new clients onboarded with relevant details such as onboarding date and industry.
        Example: “5 New Clients Onboarded / Client Renewal this week: ABC Ltd (Retail), XYZ Corp (Healthcare), etc.”

**Detail Business Analysis**
    - You are analyzing a dataset that contains transaction details for various clients. The dataset includes information such as client names, types of clients, legal entities, salesforce status, industries, sub-industries, annual revenue, transaction types, payment schemes, transaction directions, transaction volumes, and transaction values. Based on this dataset, generate the five most interesting business insights by examining patterns related to client segmentation, revenue correlation with transaction volumes, differences in payment schemes used, industry trends, and transaction direction (inbound/outbound). Focus on identifying key trends, outliers, correlations, and unique characteristics within the dataset. This analysis should be for the selected Period Only.

"""
