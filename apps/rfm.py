# %%
import pandas as pd
from duckdb import connect
conn = connect()
def etl():
    df = pd.read_excel("/Users/steven/data/Online Retail.xlsx")
    conn.execute("copy(select * from df) to 'data/oneline_retail.parquet'")
# etl()
# %%
def get_rfm(countries):
    print(countries)
    if countries:
        countries =",".join([f"'{x}'" for x in countries])
        country_where = f"and Country in ({countries})"
    else:
        country_where = ""
    print(country_where)
    rfm = conn.execute(f"""
    WITH 
    --Compute for F & M
    t1 AS (
        SELECT  
        CustomerID,
        Country,
        MAX(InvoiceDate) AS last_purchase_date,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        SUM(Quantity*UnitPrice) AS monetary 
        FROM 'data/oneline_retail.parquet' WHERE CustomerID NOTNULL
        {country_where}
        GROUP BY CustomerID, Country 
    ),

    --Compute for R
    t2 AS (
        SELECT *,
        DATE_DIFF('DAYS', last_purchase_date::date, reference_date::date)+1 AS recency
        FROM (
            SELECT  *,
            MAX(last_purchase_date) OVER ()  AS reference_date
            FROM t1
        )  
    ),
    --Determine quintiles for RFM
    t3 AS (
    SELECT 
        percentile_cont([0.2, 0.4, 0.6, 0.8]) within group(order by recency )  _r
        ,percentile_cont([0.2, 0.4, 0.6, 0.8]) within group(order by frequency )  _f
        ,percentile_cont([0.2, 0.4, 0.6, 0.8]) within group(order by monetary )  _m
    FROM 
        t2
    )
    , _r as (select _r from t3)
    , _f as (select _f from t3)
    , _m as (select _m from t3)
    --  select (table _r),  (table _f),(table _m)
    , t4 as (
        SELECT *, 
        CAST(ROUND((f_score + m_score) / 2, 0) AS INT64) AS fm_score
        FROM (
            SELECT *, 
                CASE WHEN monetary <= (table _m)[1] THEN 1
                    WHEN monetary <= (table _m)[2] AND monetary > (table _m)[1] THEN 2 
                    WHEN monetary <= (table _m)[3] AND monetary > (table _m)[2] THEN 3 
                    WHEN monetary <= (table _m)[4] AND monetary > (table _m)[3] THEN 4 
                    WHEN   monetary > (table _m)[4] THEN 5
                END AS m_score,
                CASE WHEN frequency <= (table _f)[1] THEN 1
                    WHEN frequency <= (table _f)[2] AND frequency > (table _f)[1] THEN 2 
                    WHEN frequency <= (table _f)[3] AND frequency > (table _f)[2] THEN 3 
                    WHEN frequency <= (table _f)[4] AND frequency > (table _f)[3] THEN 4 
                    WHEN   frequency > (table _f)[4] THEN 5
                END AS f_score,
                --Recency scoring is reversed
                CASE WHEN recency <= (table _r)[1] THEN 5
                    WHEN recency <= (table _r)[2] AND recency > (table _r)[1] THEN 4 
                    WHEN recency <= (table _r)[3] AND recency > (table _r)[2] THEN 3 
                    WHEN recency <= (table _r)[4] AND recency > (table _r)[3] THEN 2 
                    WHEN recency > (table _r)[4] THEN 1
                END AS r_score
                    FROM t2 
            ) aa
    ),
    --Define RFM segments
    t5 AS (
        SELECT 
            CustomerID, 
            Country,
            recency,
            frequency, 
            monetary,
            r_score,
            f_score,
            m_score,
            fm_score,
            CASE WHEN (r_score = 5 AND fm_score = 5) 
                OR (r_score = 5 AND fm_score = 4) 
                OR (r_score = 4 AND fm_score = 5) 
            THEN 'Champions'
            WHEN (r_score = 5 AND fm_score =3) 
                OR (r_score = 4 AND fm_score = 4)
                OR (r_score = 3 AND fm_score = 5)
                OR (r_score = 3 AND fm_score = 4)
            THEN 'Loyal Customers'
            WHEN (r_score = 5 AND fm_score = 2) 
                OR (r_score = 4 AND fm_score = 2)
                OR (r_score = 3 AND fm_score = 3)
                OR (r_score = 4 AND fm_score = 3)
            THEN 'Potential Loyalists'
            WHEN r_score = 5 AND fm_score = 1 THEN 'Recent Customers'
            WHEN (r_score = 4 AND fm_score = 1) 
                OR (r_score = 3 AND fm_score = 1)
            THEN 'Promising'
            WHEN (r_score = 3 AND fm_score = 2) 
                OR (r_score = 2 AND fm_score = 3)
                OR (r_score = 2 AND fm_score = 2)
            THEN 'Customers Needing Attention'
            WHEN r_score = 2 AND fm_score = 1 THEN 'About to Sleep'
            WHEN (r_score = 2 AND fm_score = 5) 
                OR (r_score = 2 AND fm_score = 4)
                OR (r_score = 1 AND fm_score = 3)
            THEN 'At Risk'
            WHEN (r_score = 1 AND fm_score = 5)
                OR (r_score = 1 AND fm_score = 4)        
            THEN 'Cant Lose Them'
            WHEN r_score = 1 AND fm_score = 2 THEN 'Hibernating'
            WHEN r_score = 1 AND fm_score = 1 THEN 'Lost'
            END AS rfm_segment 
        FROM t4
    )

    SELECT * FROM t5
    """).df()
    return rfm
# %%
#![](https://miro.medium.com/max/1400/1*fb5x_3Gi0m4c4kqTD9TV3g.webp)
# %%
# Topline Performance on Key Metrics
import panel as pn 
pn.extension('tabulator')


country = conn.execute("select Country from 'data/oneline_retail.parquet' group by all").df()

multi_choice = pn.widgets.select.CrossSelector(name='Country',
    options=list(country.Country))

@pn.depends(multi_choice.param.value)
def update_plot(countries):
    print(countries)
    rfm = get_rfm(countries)
    df1 = conn.execute("""select count(*) cnt
                        ,sum(monetary) sales
                        ,sum(monetary)/sum(frequency) as avg_m
                        ,sum(frequency)/count(*) as avg_f
                    from rfm """).df()
    a = pn.pane.HTML(f"<center size=1># of Customer<br/><h2>{df1['cnt'][0]/1000}K</h2></center>",
    width=150, height=80, background='#eeeeee', margin=10)

    b = pn.pane.HTML(f"<center size=1>Total Sales<br/><h2>{round(df1['sales'][0]/1000000,3)}M</h2></center>",
    width=150, height=80, background='#eeeeee', margin=10)

    c = pn.pane.HTML(f"<center size=1>Avg Price Per Purchase<br/><h2>{round(df1['avg_m'][0],3)}</h2></center>",
    width=150, height=80, background='#eeeeee', margin=10)
    d = pn.pane.HTML(f"<center size=1>Avg Frequency of Buying<br/><h2>{round(df1['avg_f'][0],3)}</h2></center>",
    width=150, height=80, background='#eeeeee', margin=10)

    layout = pn.Row(a, b, c,d)

    # %%
    # RFM Segment Sizes
    df =conn.execute("""select rfm_segment,count(*) cnt 
                        ,sum(monetary) "Total Sales"
                        ,sum(monetary)/sum(frequency) as monetary
                        ,sum(frequency)/count(*) as frequency
                        ,sum(recency) /count(*) as recency
                    from rfm group by all""").df()
    import hvplot.pandas
    #df = conn.execute("select recency x , frequency y ,rfm_segment,count(*) as cnt from rfm group by all order by 4 desc ").df()

    # %%
    plot_bubble=df.hvplot.scatter(x="recency", y="frequency", s=df["monetary"]*2 ,
    by='rfm_segment',legend="left",height=400)
    # %%

    # print(df.columns)

    tabulator_formatters = {
        'monetary': {'type': 'progress', 'max': 500,'color':'red'},
        'frequency': {'type': 'progress', 'max': 10,'color':'pink'},
        'recency': {'type': 'progress', 'max': 200,'color':'aqua'},
        'bool': {'type': 'tickCross'}
    }

    tabedit = pn.widgets.Tabulator(
        value=df, show_index=False, selectable=True, 
        disabled=True, theme="site", height=600,
        formatters=tabulator_formatters
    )
    # tabedit
    # %%
    return pn.Column(
        pn.Column(pn.Row(pn.Column(multi_choice, height=200,width=500))),
        pn.Column("## Topline Performance on Key Metrics",layout),
        pn.Column("## RFM Segment Sizes",plot_bubble),
        pn.Column("## Detailed Recency, Frequency, and Monetary Data",tabedit),
    )
header = pn.pane.Markdown("# RFM Segmentation Dashboard",style={'background-color':'silver'})
pn.Column(header,update_plot).servable()
# %%
