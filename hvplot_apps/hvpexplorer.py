# %%
import hvplot.pandas
from bokeh.sampledata import penguins

df = penguins.data
# df.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
# %%
hvexplorer = hvplot.explorer(df)
# %%
# type(hvexplorer)
# %%
# dir(hvexplorer)
# %%
xx =hvexplorer.__panel__()
# %%
xx.servable()