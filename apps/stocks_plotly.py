# pip install plotly
import panel as pn
pn.extension('plotly')
import pandas as pd
import plotly.graph_objects as go

from bokeh.sampledata import stocks



title = '## Stock Explorer Plotly'

tickers = ['AAPL', 'FB', 'GOOG', 'IBM', 'MSFT']

def get_df(ticker, window_size):
    df = pd.DataFrame(getattr(stocks, ticker))
    df['date'] = pd.to_datetime(df.date)
    return df.set_index('date').rolling(window=window_size).mean().reset_index()

def get_plot(ticker, window_size):
    df = get_df(ticker, window_size)
    return go.Scatter(x=df.date, y=df.close)
ticker = pn.widgets.Select(name='Ticker', options=tickers)
window = pn.widgets.IntSlider(name='Window Size', value=6, start=1, end=21)

def get_plot(ticker, window_size):
    df = get_df(ticker, window_size)
    return go.Scatter(x=df.date, y=df.close)

pn.Row(
    pn.Column(title, ticker, window),
    pn.bind(get_plot, ticker, window),
    sizing_mode='stretch_width'
).servable()