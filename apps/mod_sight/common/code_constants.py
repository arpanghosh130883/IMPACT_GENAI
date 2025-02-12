ACCOUNTS_ANALYSIS_CODE = """
# Plotting the number of open accounts, new accounts, and transacting accounts over time in the same visual

# Import necessary libraries
import matplotlib.pyplot as plt
import pandas as pd

# Convert 'MONTH_END_DATE' to datetime format, assuming it's in 'year-month-day' format
df['MONTH_END_DATE'] = pd.to_datetime(df['MONTH_END_DATE'], format='%Y-%m-%d')
dates = df['MONTH_END_DATE']

# Create a new figure for the line chart
plt.figure(figsize=(14, 8))

# Plot the number of open accounts as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_OPEN_ACCOUNTS'], label='Open Accounts', color='blue', marker='o', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_OPEN_ACCOUNTS']):
    plt.text(dates[i], df['NUMBER_OF_OPEN_ACCOUNTS'][i] + 2, str(txt), ha='center', va='bottom', fontsize=8, color='blue')

# Plot the number of new accounts as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_NEW_ACCOUNTS'], label='New Accounts', color='orange', marker='s', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_NEW_ACCOUNTS']):
    plt.text(dates[i], df['NUMBER_OF_NEW_ACCOUNTS'][i] + 2, str(txt), ha='center', va='bottom', fontsize=8, color='orange')

# Plot the number of transacting accounts as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_TRANSACTING_ACCOUNTS'], label='Transacting Accounts', color='green', marker='^', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_TRANSACTING_ACCOUNTS']):
    plt.text(dates[i], df['NUMBER_OF_TRANSACTING_ACCOUNTS'][i] + 2, str(txt), ha='center', va='bottom', fontsize=8, color='green')

# Adding labels and title
plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Accounts Analysis: Open, New, and Transacting Accounts Over Time')
plt.legend()

# Format the x-axis to display month and year (e.g., 'Aug 2027')
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %Y'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to fit everything nicely
plt.tight_layout()

# Save and show the plot
plt_path_accounts_comparison_all = "/mnt/data/Accounts_Comparison_All.png"
plt.savefig(plt_path_accounts_comparison_all)
plt.show()

"""


TRANSACTION_REVENUE_CODE ="""
# Transactions and Revenue: Transaction Volume and Transaction Value Over Time

# Import necessary libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Ensure 'MONTH_END_DATE' is in datetime format
df['MONTH_END_DATE'] = pd.to_datetime(df['MONTH_END_DATE'], format='%Y-%m-%d')

# Create a new figure for the line chart
plt.figure(figsize=(14, 8))

# Plotting Transaction Volume on the primary y-axis
color = 'tab:blue'
plt.plot(df['MONTH_END_DATE'], df['TRANSACTION_VOLUME'], color=color, marker='o', linestyle='-', label='Transaction Volume')
for i, txt in enumerate(df['TRANSACTION_VOLUME']):
    plt.text(df['MONTH_END_DATE'][i], df['TRANSACTION_VOLUME'][i] + 10, str(txt), ha='center', va='bottom', fontsize=8, color=color)

# Plotting Transaction Value on the secondary y-axis
ax2 = plt.gca().twinx()
color = 'tab:red'
# Converting Transaction Value to millions for better readability
transaction_value_millions = df['TRANSACTION_VALUE_GBP'] / 1e6
ax2.plot(df['MONTH_END_DATE'], transaction_value_millions, color=color, marker='s', linestyle='-', label='Transaction Value')
for i, txt in enumerate(transaction_value_millions):
    ax2.text(df['MONTH_END_DATE'][i], transaction_value_millions[i] + 0.1, f'{txt:.2f}', ha='center', va='bottom', fontsize=8, color=color)

# Adding axis labels and title
plt.xlabel('Month')  # Set x-axis label to "Month"
plt.ylabel('Transaction Volume')
ax2.set_ylabel('Transaction Value (in Millions GBP)', color=color)
plt.title('Transaction Volume and Transaction Value Over Time')

# Formatting x-axis to show month and year (e.g., 'Aug 2027')
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show every third month
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Force a redraw of the x-axis to apply formatting
plt.gca().figure.canvas.draw()  # Force a redraw of the figure to apply changes


# Save and show the plot
plt_path_corrected_transaction_volume_value = "/mnt/data/corrected_transaction_volume_and_value.png"
plt.savefig(plt_path_corrected_transaction_volume_value)
plt.show()



"""

CUSTOMER_ANALYSIS_CODE ="""
# Summarizing the number of transacting customers bottom value correction

import matplotlib.pyplot as plt
import pandas as pd

# Ensure 'MONTH_END_DATE' is in datetime format
df['MONTH_END_DATE'] = pd.to_datetime(df['MONTH_END_DATE'], format='%Y-%m-%d')
dates = df['MONTH_END_DATE']

# Create a new figure for the line chart
plt.figure(figsize=(14, 8))

# Plot the number of customers as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_CUSTOMERS'], label='Customers', color='green', marker='o', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_CUSTOMERS']):
    plt.text(dates[i], df['NUMBER_OF_CUSTOMERS'][i], str(txt), ha='center', va='bottom', fontsize=8, color='green')

# Plot the number of new customers as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_NEW_CUSTOMERS'], label='New Customers', color='orange', marker='s', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_NEW_CUSTOMERS']):
    plt.text(dates[i], df['NUMBER_OF_NEW_CUSTOMERS'][i], str(txt), ha='center', va='bottom', fontsize=8, color='orange')

# Plot the number of transacting customers as a line with markers and text labels
plt.plot(dates, df['NUMBER_OF_TRANSACTING_CUSTOMERS'], label='Transacting Customers', color='blue', marker='^', linestyle='-')
for i, txt in enumerate(df['NUMBER_OF_TRANSACTING_CUSTOMERS']):
    plt.text(dates[i], df['NUMBER_OF_TRANSACTING_CUSTOMERS'][i], str(txt), ha='center', va='bottom', fontsize=8, color='blue')

# Adding labels and title
plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Customer Analysis: Customers, New Customers, and Transacting Customers Over Time')
plt.legend()

# Format the x-axis to display month and year (e.g., 'Aug 2023')
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %Y'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Adjust layout to fit everything nicely
plt.tight_layout()

# Save and show the plot
plt_path_customers_line_chart = "/mnt/data/Customers_Line_Chart.png"
plt.savefig(plt_path_customers_line_chart)
plt.show()

"""

FRAUD_ANALYSIS_CODE ="""
# Fraud Analysis: Inbound Fraud Volume vs. Value Over Time

# Import necessary libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Ensure 'MONTH_END_DATE' is in datetime format
df['MONTH_END_DATE'] = pd.to_datetime(df['MONTH_END_DATE'], format='%Y-%m-%d')

# Create a new figure for the line chart
plt.figure(figsize=(14, 8))

# Plotting Inbound Fraud Volume on the primary y-axis
color = 'tab:blue'
plt.plot(df['MONTH_END_DATE'], df['INBOUND_APP_FRAUD_VOLUME'], color=color, marker='o', linestyle='-', label='Inbound Fraud Volume')
for i, txt in enumerate(df['INBOUND_APP_FRAUD_VOLUME']):
    plt.text(df['MONTH_END_DATE'][i], df['INBOUND_APP_FRAUD_VOLUME'][i] + 50, str(txt), ha='center', va='bottom', fontsize=8, color=color)

# Plotting Inbound Fraud Value on the secondary y-axis
ax2 = plt.gca().twinx()
color = 'tab:red'
# Converting Inbound Fraud Value to millions for better readability
inbound_fraud_value_millions = df['INBOUND_APP_FRAUD_VALUE_GBP'] / 1e6
ax2.plot(df['MONTH_END_DATE'], inbound_fraud_value_millions, color=color, marker='s', linestyle='-', label='Inbound Fraud Value')
for i, txt in enumerate(inbound_fraud_value_millions):
    ax2.text(df['MONTH_END_DATE'][i], inbound_fraud_value_millions[i] + 0.2, f'{txt:.2f}', ha='center', va='bottom', fontsize=8, color=color)

# Adding axis labels and title
plt.xlabel('Month')  # Set x-axis label to "Month"
plt.ylabel('Inbound Fraud Volume', color='tab:blue')
ax2.set_ylabel('Inbound Fraud Value (in Millions GBP)', color='tab:red')
plt.title('Fraud Analysis: Inbound Fraud Volume and Value Over Time')

# Formatting x-axis to show month and year (e.g., 'Jan 2023')
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show every third month
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Force a redraw of the x-axis to apply formatting
plt.gca().figure.canvas.draw()  # Force a redraw of the figure to apply changes

# Adjust layout with more padding for x-axis label visibility
plt.tight_layout(pad=4.0)

# Save and show the plot
plt_path_fraud_analysis = "/mnt/data/fraud_analysis_volume_value.png"
plt.savefig(plt_path_fraud_analysis)
plt.show()


"""


REVENUE_FORECAST_CODE ="""
# Revenue and Forecast: Clean Transaction Revenue, Clean Minimum Top-Up, and Forecast Revenue Over Time

# Import necessary libraries
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Ensure 'MONTH_END_DATE' is in datetime format
df['MONTH_END_DATE'] = pd.to_datetime(df['MONTH_END_DATE'], format='%Y-%m-%d')

# Create a figure and axis objects for dual y-axes
fig, ax1 = plt.subplots(figsize=(14, 8))

# Plotting Clean Transaction Revenue on the primary y-axis
color = 'tab:blue'
ax1.set_xlabel('Month')  # Set x-axis label to "Month"
ax1.set_ylabel('GBP (Transaction Revenue and Top-Up)', color=color)
ax1.plot(df['MONTH_END_DATE'], df['CLEAN_TRANSACTION_REVENUE_GBP'], color=color, marker='o', linestyle='-', label='Clean Transaction Revenue')
for i, txt in enumerate(df['CLEAN_TRANSACTION_REVENUE_GBP']):
    ax1.text(df['MONTH_END_DATE'][i], df['CLEAN_TRANSACTION_REVENUE_GBP'][i], f'{txt:,.0f}', ha='center', va='bottom', fontsize=8, color=color)

# Plotting Clean Minimum Top-Up on the primary y-axis
color = 'tab:green'
ax1.plot(df['MONTH_END_DATE'], df['CLEAN_MINIMUM_TOP_UP_GBP'], color=color, marker='s', linestyle='-', label='Clean Minimum Top-Up')
for i, txt in enumerate(df['CLEAN_MINIMUM_TOP_UP_GBP']):
    ax1.text(df['MONTH_END_DATE'][i], df['CLEAN_MINIMUM_TOP_UP_GBP'][i], f'{txt:,.0f}', ha='center', va='bottom', fontsize=8, color=color)

ax1.tick_params(axis='y', labelcolor='tab:blue')

# Plotting Forecast Revenue on the secondary y-axis
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Forecast Revenue (in GBP)', color=color)
ax2.plot(df['MONTH_END_DATE'], df['FORECAST_REVENUE_GBP'], color=color, marker='^', linestyle='-', label='Forecast Revenue')
for i, txt in enumerate(df['FORECAST_REVENUE_GBP']):
    ax2.text(df['MONTH_END_DATE'][i], df['FORECAST_REVENUE_GBP'][i], f'{txt:,.0f}', ha='center', va='bottom', fontsize=8, color=color)

ax2.tick_params(axis='y', labelcolor=color)

# Adding axis labels and title
plt.title('Clean Transaction Revenue, Clean Minimum Top-Up, and Forecast Revenue Over Time')

# Formatting x-axis to show month and year (e.g., 'Jan 2023')
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show every third month
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Add a legend in a clean, out-of-the-way location
fig.legend(loc="upper left", bbox_to_anchor=(-0.1, 1), fontsize=10)

# Adjust layout for better spacing and readability
fig.tight_layout()

# Save the plot and display
plt_path_corrected_revenue_forecast_same_axis = "/mnt/data/corrected_revenue_forecast_same_axis.png"
plt.savefig(plt_path_corrected_revenue_forecast_same_axis)
plt.show()


"""