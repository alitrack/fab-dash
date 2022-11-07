# pip install altair vega
import panel as pn
import pandas as pd
import altair as alt
from bokeh.sampledata import stocks
# pn.extension("vega")
# pn.extension('vega', template='fast-list')


title = '## Stock Explorer Altair'

tickers = ['AAPL', 'FB', 'GOOG', 'IBM', 'MSFT']

def get_df(ticker, window_size):
    df = pd.DataFrame(getattr(stocks, ticker))
    df['date'] = pd.to_datetime(df.date)
    return df.set_index('date').rolling(window=window_size).mean().reset_index()

def get_plot(ticker, window_size):
    df = get_df(ticker, window_size)
    return alt.Chart(df).mark_line().encode(x='date', y='close').properties(width="container", height="container")

interact = pn.interact(get_plot, ticker=tickers, window_size=(1, 21, 5))

pn.Row(
    pn.Column(title, interact[0]),
    interact[1]
).servable()

