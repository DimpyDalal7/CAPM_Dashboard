# importing libraries

import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import capm_functions
import numpy as np

st.set_page_config(page_title="CAPM",page_icon='chart_with_upwards_trend',layout='wide')
st.title("Capital Asset Pricing Model")

# getting input from user

top_50 = ["AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "FB", "TSLA", "BRK.A", "BRK.B", "NVDA","JPM", "JNJ", "V", "HD", "PG", "MA", "UNH", "BAC", "PYPL", "DIS",    "INTC", "VZ", "ADBE", "NFLX", "T", "MRK", "KO", "CSCO", "CMCSA", "XOM",    "CVX", "PFE", "WMT", "ABT", "PDD", "MCD", "NKE", "TMO", "ORCL", "AMGN",    "CRM", "PEP", "TMO", "TGT", "ABBV", "NVAX", "BMY", "JNJ", "TXN", "UNP"]

col1,col2=st.columns([1,1])
with col1:
    stocks_list=st.multiselect('Choose 4 stocks',top_50,['TSLA','AAPL','AMZN','GOOGL'])
with col2:
    year=st.number_input("number of years",1,10)

# downloading data for s&p500

import datetime

try:

    end=datetime.date.today()
    start=datetime.date(datetime.date.today().year-year,datetime.date.today().month,datetime.date.today().day)
    SP500=web.DataReader(['sp500'],'fred',start,end)
    print(SP500.head())

    # downloading data for the selected stocks

    stocks_df=pd.DataFrame()

    for stock in stocks_list:
        data=yf.download(stock,period=f'{year}y')
        stocks_df[f'{stock}']=data['Close']

    # to merge both the dataframes, index should be made of same datatype
    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns=['Date','S&P500']

    # checking the datatypes of columns of both the fataframes

    print(stocks_df.dtypes)
    print(SP500.dtypes)

    print(stocks_df.head())
    print(SP500.head())

    # columns of both dataframes have same datatype so we can merge them now

    stocks_df=pd.merge(stocks_df,SP500,on='Date',how='inner')
    print(stocks_df)

    table=stocks_df.reset_index(drop=True)

    st.markdown('### Stocks Price')
    st.dataframe(table,use_container_width=True,height=200)

    col1,col2=st.columns([1,1])
    with col1:
        st.markdown('### Stocks Trend')
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))
    with col2:
        st.markdown('### Stocks Trend after Normalization')
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    stocks_daily_return=capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta={}
    alpha={}

    for i in stocks_daily_return.columns:
        if i!='Date' and i!='S&P500':
            b,a= capm_functions.calculate_beta(stocks_daily_return,i)
            beta[i]=b
            alpha[i]=a
    print(beta,alpha)

    beta_df=pd.DataFrame(columns=['Stock','Beta Value'])
    beta_df['Stock']=beta.keys()
    beta_df['Beta Value']=[str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown('### Caculated Beta Value')
        st.dataframe(beta_df,use_container_width=True)

    rf=0
    rm=stocks_daily_return['S&P500'].mean()*252

    return_df=pd.DataFrame()
    return_value=[]
    for stock, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf)),2)))
    return_df['Stock']=stocks_list
    return_df['Return Value']=return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df,use_container_width=True)

except:
    st.write('Please select valid inputs')