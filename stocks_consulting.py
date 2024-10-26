from datetime import *
import pandas as pd
import streamlit as st
import warnings
from yahoofinancials import YahooFinancials

warnings.simplefilter(action='ignore', category=FutureWarning)

def get_previous_day():
    previous_day = str(date.today() - timedelta(days=1))
    return previous_day

def request_data(ticker):
    yf = YahooFinancials(ticker)
    try:
        data_income = yf.get_financial_stmts('annual', 'income')['incomeStatementHistory'][ticker]
        data_cash = yf.get_financial_stmts('annual', 'cash')['cashflowStatementHistory'][ticker]
        data_balance = yf.get_financial_stmts('annual', 'balance')['balanceSheetHistory'][ticker]
        stock_history = yf.get_historical_price_data(
            start_date=get_previous_day(), 
            end_date=str(date.today()), 
            time_interval="daily")[ticker]
        return data_income, data_cash, data_balance, stock_history
    except Exception as e:
        return None, None, None, None  # Return None for all data if there's an error

def get_most_recent_report(data):
    all_dates = [key for dico in data if dico for key in dico.keys()]
    if not all_dates:  # Check if there are no dates
        return {}
    max_date = max(all_dates)
    report_last_date = next((entry for entry in data if max_date in entry), None)
    return report_last_date[max_date] if report_last_date else {}


def get_turnover():
    turnover = get_most_recent_report(data_income)['totalRevenue']
    return str(round(turnover, 2)) + " $"

def get_free_cash_flow():
    free_cash_flow = get_most_recent_report(data_cash)['freeCashFlow']
    return str(round(free_cash_flow, 2)) + " $"

def get_gross_margin():
    turnover = get_most_recent_report(data_income)['totalRevenue']
    gross_profit = get_most_recent_report(data_income)['grossProfit']
    gross_margin = gross_profit / turnover * 100
    return str(round(gross_margin, 2)) + " %"

def get_net_turnover():
    net_turnover = get_most_recent_report(data_income)['netIncome']
    return str(round(net_turnover, 2)) + " $"

def get_net_margin():
    net_turnover = get_most_recent_report(data_income)['netIncome']
    turnover = get_most_recent_report(data_income)['totalRevenue']
    net_margin = net_turnover / turnover * 100
    return str(round(net_margin, 2)) + " %"

def get_roe():
    stockholders_equity = get_most_recent_report(data_balance)['stockholdersEquity']
    net_turnover = get_most_recent_report(data_income)['netIncome']
    roe = net_turnover / stockholders_equity * 100
    return str(round(roe, 2)) + " %"

def get_operating_margin():
    ebit = get_most_recent_report(data_income)['ebit']
    turnover = get_most_recent_report(data_income)['totalRevenue']
    operating_margin = ebit / turnover * 100
    return str(round(operating_margin, 2)) + " %"

def get_roa():
    total_assets = get_most_recent_report(data_balance)['totalAssets']
    net_turnover = get_most_recent_report(data_income)['netIncome']
    roa = net_turnover / total_assets * 100
    return str(round(roa, 2)) + " %"

def get_payout_ratio():
    total_dividend_paid = get_most_recent_report(data_cash).get('cashDividendsPaid', 0)  # Default to 0 if not found
    net_turnover = get_most_recent_report(data_income)['netIncome']
    if net_turnover == 0:  # Avoid division by zero
        return "N/A"  # Or some suitable default value
    payout_ratio = - total_dividend_paid / net_turnover * 100
    return str(round(payout_ratio, 2)) + " %"


def get_ratio_equity_debt():
    stockholders_equity = get_most_recent_report(data_balance)['stockholdersEquity']
    debt = get_most_recent_report(data_balance)['longTermDebt']
    ratio_debt_equity = debt / stockholders_equity * 100
    return str(round(ratio_debt_equity, 2)) + " %"

def get_per():
    total_cap = get_most_recent_report(data_balance)['totalCapitalization']
    net_turnover = get_most_recent_report(data_income)['netIncome']
    per = total_cap / net_turnover * 100
    return str(round(per, 2)) + " %"

def get_today_stock():
    return str(round(stock_history['prices'][0]['close'], 2)) + " $"

# Streamlit App Layout
st.title("Stocks Consulting")
st.write("Welcome to the Stocks Consulting page!")
st.write("This page consists of indicators and information about company stocks.")
st.write("--------------------------------------------------------")

ticker = st.text_input('Enter your ticker please:', '')

if st.button('Get Stock Data'):
    data_income, data_cash, data_balance, stock_history = request_data(ticker.strip())
    
    if data_income is None or data_cash is None or data_balance is None or stock_history is None:
        st.error("Failed to retrieve data for the provided ticker.")
    else:
        indicators = {
            "Today Stock Price": get_today_stock(),
            "Turnover": get_turnover(),
            "Net Turnover": get_net_turnover(),
            "Gross Margin": get_gross_margin(),
            "Net Margin": get_net_margin(),
            "Operating Margin": get_operating_margin(),
            "ROE (Return on Equity)": get_roe(),
            "ROA (Return on Assets)": get_roa(),
            "Payout Ratio": get_payout_ratio(),
            "PER (Price Earnings Ratio)": get_per(),
            "Free Cash Flow": get_free_cash_flow(),
            "Ratio Debt/Equity": get_ratio_equity_debt(),
        }
        
        for indicator, value in indicators.items():
            st.write(f"{indicator}: {value}")

st.write("--------------------------------------------------------")
