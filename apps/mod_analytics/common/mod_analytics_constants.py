session_state_page1 = "chat_with_external_data_messages"
session_state_page2 = "chat_with_impact_data_messages"

CI_PROMPT = f"""Analyze the provided data and generate insightful visualizations and data analysis for the following categories:
Task: After displaying the visuals, provide an in-depth data analysis for each chart, focusing on meaningful insights rather than just describing the colors and aesthetics. The prompt should guide the interpretation of the data trends, patterns, and relationships based on the plot visuals.
Note: Do not mention or describe the cleaning process.
"""