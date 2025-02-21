import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Leningcalculator")

# Sidebar inputs blijven hetzelfde
with st.sidebar:
    loan_amount = st.slider("Leenbedrag (€)", min_value=50000, max_value=1000000, value=500000, step=50000, format="%d")
    loan_term = st.slider("Looptijd (jaren)", min_value=1, max_value=15, value=10)
    interest_rate_lin = st.slider("Rente Lin (%)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    interest_rate_2024_2025 = st.slider("Rente 2024 & 2025 (%)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    success_fee = st.slider("Succesfee 2025 (%)", min_value=1.0, max_value=8.0, value=4.0, step=0.5)
    management_fee = st.slider("Beheerfee 2025 (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.1)

# Berekeningsfuncties
def calculate_tiered_fee(amount):
    fee = 0
    if amount <= 300000:
        fee += amount * 0.08
    else:
        fee += 300000 * 0.08
        if amount <= 600000:
            fee += (amount - 300000) * 0.06
        else:
            fee += 300000 * 0.06
            if amount <= 800000:
                fee += (amount - 600000) * 0.04
            else:
                fee += 200000 * 0.04
                if amount <= 1000000:
                    fee += (amount - 800000) * 0.03
                else:
                    fee += 200000 * 0.03
                    fee += (amount - 1000000) * 0.02
    return fee

# Bereken jaarlijkse kosten voor de grafiek
def calculate_yearly_costs():
    years = list(range(1, loan_term + 1))
    costs_lin = []
    costs_2024 = []
    costs_2025 = []
    
    for year in years:
        # Lin scenario
        monthly_payment = loan_amount / (loan_term * 12)
        remaining_loan_lin = loan_amount - (monthly_payment * 12 * (year - 1))
        yearly_interest_lin = remaining_loan_lin * (interest_rate_lin / 100)
        costs_lin.append(yearly_interest_lin)
        
        # 2024 scenario
        yearly_payment = loan_amount / loan_term
        remaining_loan_2024 = loan_amount - (yearly_payment * (year - 1))
        yearly_interest_2024 = remaining_loan_2024 * (interest_rate_2024_2025 / 100)
        tiered_fee = calculate_tiered_fee(loan_amount) if year == 1 else 0
        costs_2024.append(yearly_interest_2024 + tiered_fee)
        
        # 2025 scenario
        remaining_loan_2025 = loan_amount - (yearly_payment * (year - 1))
        yearly_interest_2025 = remaining_loan_2025 * (interest_rate_2024_2025 / 100)
        success_fee_yearly = (loan_amount * success_fee / 100) if year == 1 else 0
        management_fee_yearly = remaining_loan_2025 * (management_fee / 100) if year > 1 else 0
        costs_2025.append(yearly_interest_2025 + success_fee_yearly + management_fee_yearly)
    
    return years, costs_lin, costs_2024, costs_2025

# Berekeningen voor Lin scenario
def calculate_lin_interest():
    total_interest = 0
    for year in range(1, loan_term + 1):
        monthly_payment = loan_amount / (loan_term * 12)
        remaining_loan = loan_amount - (monthly_payment * 12 * (year - 1))
        total_interest += (remaining_loan * (interest_rate_lin / 100))
    return total_interest

# Berekeningen voor 2024 scenario
def calculate_2024_interest():
    total_interest = 0
    for year in range(1, loan_term + 1):
        yearly_payment = loan_amount / loan_term
        remaining_loan = loan_amount - (yearly_payment * (year - 1))
        total_interest += (remaining_loan * (interest_rate_2024_2025 / 100))
    return total_interest

# Berekeningen voor 2025 scenario
def calculate_2025_interest():
    total_interest = 0
    total_management_fee = 0
    for year in range(1, loan_term + 1):
        yearly_payment = loan_amount / loan_term
        remaining_loan = loan_amount - (yearly_payment * (year - 1))
        total_interest += (remaining_loan * (interest_rate_2024_2025 / 100))
        if year > 1:  # Beheerfee vanaf jaar 2
            total_management_fee += (remaining_loan * (management_fee / 100))
    return total_interest, total_management_fee

# Bereken alle waardes
total_interest_lin = calculate_lin_interest()
total_interest_2024 = calculate_2024_interest()
tiered_fee_2024 = calculate_tiered_fee(loan_amount)
total_interest_2025, total_management_fee = calculate_2025_interest()
success_fee_2025 = loan_amount * (success_fee / 100)

# Maak drie kolommen voor de resultaten
col1, col2, col3 = st.columns(3)

# Scenario Lin
with col1:
    st.subheader("Scenario Lin")
    st.write("Leenbedrag:", f"€{loan_amount:,.0f}")
    st.write("Totale rente:", f"€{total_interest_lin:,.0f}")
    total_lin = loan_amount + total_interest_lin
    st.write("**Totaal:**", f"€{total_lin:,.0f}")

# Scenario 2024
with col2:
    st.subheader("Scenario 2024")
    st.write("Leenbedrag:", f"€{loan_amount:,.0f}")
    st.write("Totale rente:", f"€{total_interest_2024:,.0f}")
    st.write("Succesfee:", f"€{tiered_fee_2024:,.0f}")
    total_2024 = loan_amount + total_interest_2024 + tiered_fee_2024
    st.write("**Totaal:**", f"€{total_2024:,.0f}")

# Scenario 2025
with col3:
    st.subheader("Scenario 2025")
    st.write("Leenbedrag:", f"€{loan_amount:,.0f}")
    st.write("Totale rente:", f"€{total_interest_2025:,.0f}")
    st.write("Succesfee:", f"€{success_fee_2025:,.0f}")
    st.write("Tot. beheerfee:", f"€{total_management_fee:,.0f}")
    total_fees = success_fee_2025 + total_management_fee
    st.write("Totaal fees:", f"€{total_fees:,.0f}")
    total_2025 = loan_amount + total_interest_2025 + success_fee_2025 + total_management_fee
    st.write("**Totaal:**", f"€{total_2025:,.0f}")

# Maak de grafiek
years, costs_lin, costs_2024, costs_2025 = calculate_yearly_costs()

# Creëer een plotly figuur
fig = go.Figure()

# Voeg de lijnen toe
fig.add_trace(go.Scatter(x=years, y=costs_lin, name='Lin', line=dict(color='rgb(136, 132, 216)')))
fig.add_trace(go.Scatter(x=years, y=costs_2024, name='2024', line=dict(color='rgb(130, 202, 157)')))
fig.add_trace(go.Scatter(x=years, y=costs_2025, name='2025', line=dict(color='rgb(255, 198, 88)')))

# Update layout
fig.update_layout(
    title='Jaarlijkse kosten per scenario',
    xaxis_title='Jaren',
    yaxis_title='Kosten (€)',
    hovermode='x unified',
    showlegend=True
)

# Toon de grafiek
st.plotly_chart(fig, use_container_width=True)
