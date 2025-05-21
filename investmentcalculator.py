import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Compound Interest Calculator
def calculate_investment(starting_amount, annual_contribution, years, rate, compound='annually'):
    balance = starting_amount
    schedule = []
    
    for year in range(1, years + 1):
        balance += annual_contribution
        interest = balance * rate
        balance += interest
        total_deposit = starting_amount + annual_contribution * year
        schedule.append({
            'Year': year,
            'Deposit': annual_contribution if year > 1 else annual_contribution + starting_amount,
            'Interest': interest,
            'Ending balance': balance
        })
    return pd.DataFrame(schedule), balance

# Streamlit UI
st.title("💰 Investment Growth Calculator")

st.sidebar.header("Input Parameters")
start_amt = st.sidebar.number_input("Starting Amount", min_value=0.0, value=20000.0, step=1000.0)
years = st.sidebar.number_input("Investment Length (years)", min_value=1, value=10)
rate = st.sidebar.number_input("Return Rate (%)", min_value=0.0, value=6.0) / 100
annual_contribution = st.sidebar.number_input("Annual Contribution", min_value=0.0, value=1000.0)

# Calculate button
if st.button("📈 Calculate"):
    df, final_balance = calculate_investment(start_amt, annual_contribution, years, rate)

    st.subheader("📊 Results")
    st.metric("End Balance", f"${final_balance:,.2f}")
    st.metric("Total Contributions", f"${start_amt + annual_contribution * years:,.2f}")
    st.metric("Total Interest", f"${final_balance - (start_amt + annual_contribution * years):,.2f}")

    st.subheader("📅 Accumulation Schedule")
    st.dataframe(df.set_index('Year'), use_container_width=True)

    # Plot
    st.subheader("📈 Growth Over Time")
    fig, ax = plt.subplots()
    ax.bar(df['Year'], df['Deposit'].cumsum(), label="Contributions", color="green")
    ax.bar(df['Year'], df['Interest'].cumsum(), bottom=df['Deposit'].cumsum(), label="Interest", color="red")
    ax.axhline(y=final_balance, color='blue', linestyle='--', label="Final Balance")
    ax.set_ylabel("Amount ($)")
    ax.legend()
    st.pyplot(fig)

# Placeholder for Gemma integration
st.markdown("🧠 *Gemma integration coming soon to allow natural language financial planning queries!*")
