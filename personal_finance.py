import streamlit as st
import re
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.title("Personal Finance Calculator")
    st.write("Calculate your monthly savings, total expenses, and get budget insights and recommendations.")
    
    # User inputs for income
    income = st.number_input("Enter your monthly income", min_value=0.0, step=0.01)

    # Input for expenses
    st.subheader("Input your expenses")
    expense_input = st.text_area("Enter your expenses (format: amount category, e.g., '50 groceries'):").strip()
    
    # Budget input
    st.subheader("Set Your Monthly Budget")
    budget_input = st.text_area("Enter your budget for each category (format: category amount, e.g., 'groceries 300'):").strip()
    budget_dict = set_budget(budget_input)

    # Process expenses to categorize
    categorized_expenses = categorize_expenses(expense_input)

    # Calculate total expenses and savings
    total_expenses = sum(categorized_expenses.values())
    savings = income - total_expenses

    # Display results
    st.write(f"### Total Monthly Expenses: ${total_expenses:.2f}")
    st.write(f"### Monthly Savings: ${savings:.2f}")
    
    # Display categorized expenses
    st.write("### Categorized Expenses:")
    for category, amount in categorized_expenses.items():
        st.write(f"- **{category.capitalize()}**: ${amount:.2f}")

    # Budget Comparison
    compare_budget(categorized_expenses, budget_dict)

    # Visualize expenses
    plot_expenses(categorized_expenses)
    plot_expense_pie_chart(categorized_expenses)

    # Anomaly Detection
    detect_anomalies(categorized_expenses)

    # Call the function to generate insights and recommendations
    generate_recommendations(income, categorized_expenses, savings)
    
    # Investment Recommendations
    recommend_investments(savings)

    # Goal-Based Savings Predictions
    savings_goal = st.number_input("Enter your savings goal", min_value=0.0, step=0.01)
    if savings_goal > 0 and savings > 0:
        months_to_goal = savings_goal / savings
        st.write(f"### Months to reach your savings goal of ${savings_goal:.2f}: {months_to_goal:.2f} months")

def set_budget(budget_input):
    budget_dict = {}
    budgets = budget_input.splitlines()
    
    for budget in budgets:
        match = re.match(r"(\w+)\s+(\d+(\.\d+)?)", budget.strip())
        if match:
            category = match.group(1).lower()
            amount = float(match.group(2))
            budget_dict[category] = amount

    return budget_dict

def compare_budget(categorized_expenses, budget_dict):
    st.write("### Budget Comparison:")
    for category, amount in categorized_expenses.items():
        budget_amount = budget_dict.get(category, 0.0)
        if amount > budget_amount:
            st.write(f"- ⚠️ Over budget in **{category.capitalize()}**: ${amount:.2f} exceeds budget of ${budget_amount:.2f}")
        else:
            st.write(f"- ✅ On track in **{category.capitalize()}**: ${amount:.2f} within budget of ${budget_amount:.2f}")

def categorize_expenses(expense_input):
    # Initialize a dictionary for categorized expenses
    categories = {
        "fixed": 0.0,
        "outing": 0.0,
        "shopping": 0.0,
        "groceries": 0.0,
        "other": 0.0
    }

    # Process the input text
    expenses = expense_input.splitlines()
    
    for expense in expenses:
        match = re.match(r"(\d+(\.\d+)?)\s*(\w+)", expense.strip())
        if match:
            amount = float(match.group(1))
            category = match.group(3).lower()
            # Categorize based on keywords
            if "rent" in category or "utility" in category:
                categories["fixed"] += amount
            elif "outing" in category or "dining" in category:
                categories["outing"] += amount
            elif "shopping" in category or "clothing" in category:
                categories["shopping"] += amount
            elif "groceries" in category or "food" in category:
                categories["groceries"] += amount
            else:
                categories["other"] += amount

    return categories

def plot_expenses(categorized_expenses):
    # Plotting the categorized expenses as a bar chart
    categories = list(categorized_expenses.keys())
    amounts = list(categorized_expenses.values())

    fig, ax = plt.subplots()
    ax.bar(categories, amounts, color=['blue', 'orange', 'green', 'red', 'purple'])
    ax.set_ylabel('Amount ($)')
    ax.set_title('Categorized Monthly Expenses')
    ax.set_xticklabels(categories, rotation=45)

    # Show the plot in Streamlit
    st.pyplot(fig)

def plot_expense_pie_chart(categorized_expenses):
    # Plotting the categorized expenses as a pie chart
    categories = list(categorized_expenses.keys())
    amounts = list(categorized_expenses.values())

    # Filter out categories with zero amounts
    filtered_categories = [category for category, amount in zip(categories, amounts) if amount > 0]
    filtered_amounts = [amount for amount in amounts if amount > 0]

    if not filtered_amounts:  # If all amounts are zero, return early
        st.write("No expenses to display in the pie chart.")
        return

    fig, ax = plt.subplots()
    ax.pie(filtered_amounts, labels=filtered_categories, autopct='%1.1f%%', startangle=90,
           colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Proportion of Expenses by Category')

    # Show the plot in Streamlit
    st.pyplot(fig)


def detect_anomalies(categorized_expenses):
    # Identify anomalies in expense categories
    avg_expenses = np.mean(list(categorized_expenses.values()))
    threshold = 1.5 * avg_expenses  # 1.5 times the average as a threshold

    st.write("### Anomaly Detection:")
    for category, amount in categorized_expenses.items():
        if amount > threshold:
            st.write(f"- ⚠️ Anomaly detected in **{category.capitalize()}**: ${amount:.2f} exceeds the threshold of ${threshold:.2f}")

def generate_recommendations(income, categorized_expenses, savings):
    # Calculate the percentage of income spent on each category
    recommendations = []

    for category, amount in categorized_expenses.items():
        expense_ratio = (amount / income) * 100 if income else 0
        if category == "fixed" and expense_ratio > 50:
            recommendations.append("- Fixed expenses are more than 50% of your income. Consider negotiating rent or reducing utility usage.")
        elif category == "outing" and expense_ratio > 10:
            recommendations.append("- Outing expenses exceed 10% of your income. Cutting down on outings could help you save more.")
        elif category == "shopping" and expense_ratio > 15:
            recommendations.append("- Shopping expenses exceed 15% of your income. Prioritize essentials or set a monthly shopping limit.")
        elif category == "groceries" and expense_ratio > 20:
            recommendations.append("- Groceries expenses are high. Look for discounts, buy in bulk, or plan meals to avoid waste.")

    # Overall savings recommendations
    if savings < (income * 0.2):
        recommendations.append("- Your savings are less than 20% of your income. Consider reducing discretionary expenses to increase savings.")
    
    if savings > (income * 0.3):
        recommendations.append("👍 Great job! You are saving more than 30% of your income.")
    elif savings > (income * 0.2):
        recommendations.append("👍 Good! You are saving around 20% of your income, keep it up!")
    else:
        recommendations.append("⚠️ Consider reducing expenses to increase your monthly savings.")

    # Display insights and recommendations
    st.write("## Budget Insights and Recommendations:")
    for recommendation in recommendations:
        st.write(recommendation)

def recommend_investments(savings):
    # Simple investment recommendations based on savings amount
    st.write("### Investment Recommendations:")
    if savings < 100:
        st.write("- Consider starting with a high-yield savings account.")
    elif 100 <= savings < 1000:
        st.write("- Look into low-cost index funds or ETFs.")
    elif 1000 <= savings < 5000:
        st.write("- Consider diversifying your portfolio with stocks and bonds.")
    elif savings >= 5000:
        st.write("- Explore real estate investment trusts (REITs) or other investment vehicles for higher returns.")
    else:
        st.write("- Review your current investment options and consult a financial advisor.")

if __name__ == "__main__":
    main()
