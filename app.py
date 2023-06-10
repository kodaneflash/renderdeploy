import streamlit as st
import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np

def calculate_total_interest(price, interest_rate, loan_years, down_payment):
    loan_amount = price - down_payment
    monthly_interest_rate = (interest_rate / 100) / 12
    loan_months = loan_years * 12

    numerator = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** loan_months)
    denominator = ((1 + monthly_interest_rate) ** loan_months) - 1
    monthly_payment = numerator / denominator

    total_amount_paid = monthly_payment * loan_months
    total_interest_paid = total_amount_paid - loan_amount

    return total_interest_paid, monthly_payment

def calculate_prepayment_savings(price, interest_rate, loan_years, down_payment, prepayment_amount, num_prepayment_months):
    _, monthly_payment_original = calculate_total_interest(price, interest_rate, loan_years, down_payment)
    amortization_table_original = generate_amortization_table(price, interest_rate, loan_years, down_payment)
    total_interest_original = np.sum(amortization_table_original[:, 1])

    loan_amount = price - down_payment
    remaining_balance = loan_amount

    for _ in range(num_prepayment_months):
        monthly_interest_rate = (interest_rate / 100) / 12
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment_original - interest_payment + prepayment_amount
        remaining_balance -= principal_payment

    remaining_loan_years = int(loan_years - (num_prepayment_months / 12))
    _, monthly_payment_new = calculate_total_interest(remaining_balance, interest_rate, remaining_loan_years, 0)
    amortization_table_new = generate_amortization_table(remaining_balance, interest_rate, remaining_loan_years, 0)
    total_interest_new = np.sum(amortization_table_new[:, 1])

    interest_saved = total_interest_original - total_interest_new
    months_saved = (loan_years * 12) - (num_prepayment_months + len(amortization_table_new))

    return interest_saved, months_saved


def generate_amortization_table(price, interest_rate, loan_years, down_payment):
    loan_amount = price - down_payment
    monthly_interest_rate = (interest_rate / 100) / 12
    loan_months = loan_years * 12

    _, monthly_payment = calculate_total_interest(price, interest_rate, loan_years, down_payment)

    amortization_table = [[1,0,0,loan_amount]]
    remaining_balance = loan_amount

    for i in range(1, loan_months):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        amortization_table.append([i + 1, interest_payment, principal_payment, remaining_balance])

    return np.array(amortization_table)

def main():
    st.title("Car Loan Interest Calculator")

    st.markdown("This calculator displays the amount of interest on a loan you'd pay including graphical visualizations, and the ability to set a prepayment amount to calculate the savings in interest and reduction in loan tenure to help understand the benefits of prepayment.")
    st.markdown("## Upcoming Features")
    st.markdown("""
    
    - Prepatment amount to calculate savings in interest and reduction in loan tenure ✔️
    - Comparison tool for different loan offers
    - Refinance calculator
    - Principal remaining over time chart
    - Annual percentage rate (APR) comparison chart
    - Cumulative interest over time chart
    - Loan term comparison chart
    - Additional inputs such as credit score, down payment, trade-in value, loan fees, sales tax, insurance, and maintenance costs
    """)
    
    price = st.number_input("Enter the car's price:", min_value=0.0, step=1000.0)
    interest_rate = st.number_input("Enter the annual interest rate (as a percentage):", min_value=0.0, max_value=100.0, step=0.1)
    loan_years = st.number_input("Enter the number of years for the car loan:", min_value=0, step=1)
    down_payment = st.number_input("Enter the down payment amount (if any):", min_value=0.0, step=1000.0)

    # Add prepayment input fields
    prepayment_amount = st.number_input("Enter the prepayment amount (if any):", min_value=0.0, step=1000.0)
    num_prepayment_months = st.number_input("Enter the number of months you want to prepay for:", min_value=0, step=1)

    if st.button("Calculate"):
        total_interest_paid, _ = calculate_total_interest(price, interest_rate, loan_years, down_payment)
        st.write(f"The total amount of interest paid over the life of the loan is: ${total_interest_paid:.2f}")

                # Calculate and display prepayment savings
        if prepayment_amount > 0 and num_prepayment_months > 0:
            interest_saved, months_saved = calculate_prepayment_savings(price, interest_rate, loan_years, down_payment, prepayment_amount, num_prepayment_months)
            st.write(f"By making a prepayment of ${prepayment_amount:,.2f} for {num_prepayment_months} months, you can save ${interest_saved:,.2f} in interest and reduce the loan tenure by {months_saved} months.")

        
        amortization_table = generate_amortization_table(price, interest_rate, loan_years, down_payment)

        # Move table creation code here
        header = dict(values=["Month", "Interest Payment", "Principal Payment", "Remaining Balance"],
                      fill_color='lightgrey',
                      align='left',
                      font=dict(color='black'),
                      height=40)
        cells = dict(values=[amortization_table[:, i] for i in range(4)],
                     fill_color='lightgrey',
                     align='left',
                     font=dict(color='black'),
                     height=40)
        table = go.Table(header=header, cells=cells)

        # Update the figure to include custom height
        figure = go.Figure(data=[table], layout=go.Layout(height=len(amortization_table)*40 + 100))
        st.plotly_chart(figure)

        # Create a line chart for Interest and Principal payments
        line_chart = go.Figure()
        line_chart.add_trace(go.Scatter(x=amortization_table[:, 0], y=amortization_table[:, 1], mode="lines", name="Interest Payment"))
        line_chart.add_trace(go.Scatter(x=amortization_table[:, 0], y=amortization_table[:, 2], mode="lines", name="Principal Payment"))
        line_chart.update_layout(title="Interest and Principal Payments Over Time", xaxis_title="Month", yaxis_title="Amount ($)")
        st.plotly_chart(line_chart)

        # Create a pie chart comparing total amount paid with and without interest
        loan_amount = price - down_payment
        total_amount_paid = loan_amount + total_interest_paid
        pie_chart = go.Figure(data=[go.Pie(labels=["Total Amount Paid (with Interest)", "Car Price"],
                                           values=[total_amount_paid, price],
                                           hole=0.4)])
        pie_chart.update_layout(title="Comparison of Total Amount Paid with and without Interest")
        st.plotly_chart(pie_chart)

if __name__ == "__main__":
    main()

