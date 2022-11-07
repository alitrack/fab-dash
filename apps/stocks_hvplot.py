# pip install hvplot
import panel as pn
import pandas as pd
import hvplot.pandas

from bokeh.sampledata import stocks

# pn.extension("bokeh")

title = '## Stock Explorer hvPlot'

tickers = ['AAPL', 'FB', 'GOOG', 'IBM', 'MSFT']

def get_df(ticker, window_size):
    df = pd.DataFrame(getattr(stocks, ticker))
    df['date'] = pd.to_datetime(df.date)
    return df.set_index('date').rolling(window=window_size).mean().reset_index()

def get_plot(ticker, window_size):
    df = get_df(ticker, window_size)
    return df.hvplot.line('date', 'close', grid=True, responsive=True, height=300)

interact = pn.interact(get_plot, ticker=tickers, window_size=(1, 21, 5))

pn.Row(
    pn.Column(title, interact[0]),
    interact[1]
).servable()
