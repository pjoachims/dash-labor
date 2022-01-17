import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import html, dcc

# Read csv and delete rows without occupation or tree level (1)
df = pd.read_csv("cpsaat11.csv", skiprows=6, sep=",", thousands=r',')
df.columns = ["Occupation", "Total", "Women (%)", "White", "Black_or_african_american", "Asian", "Hispanic_or_latino", "Tree_level"]
df.loc[0, "Occupation"] = "Total"
df = df[~df.Occupation.isna()]
df = df[~df.Tree_level.isna()]
df.Tree_level = df.Tree_level.astype(int)
df["Parent"] = "None"
df.reset_index(inplace=True, drop=True)
df.Total = df.Total.astype(int)

# Replace "-" with 50 for women?
df.loc[df["Women (%)"] == '–', "Women (%)"] = 50
df["Women (%)"] = df["Women (%)"].astype(float)

# Find parents for all elements
for i, occ in df.iterrows():
    idx_parent = np.argwhere((df.loc[:i, "Tree_level"] == (occ.Tree_level - 1)).values)
    try:
        df.loc[i, "Parent"] = df.loc[idx_parent[-1][0], "Occupation"]
    except IndexError:
        df.loc[i, "Parent"] = ""

# Make sure total is sum of childs
for level in [4, 3, 2, 1, 0]:
    df_tmp = df[df["Tree_level"] == level]
    for i, occ in df_tmp.iterrows():
        childs = (df.Parent == occ.Occupation)
        if (childs).sum() > 0:
            df.loc[i, "Total"] = df[childs].Total.sum()

# Make sunburst plot
fig = px.sunburst(
    df,
    names="Occupation",
    parents="Parent",
    values="Total",
    branchvalues="total",
    color_continuous_scale='RdYlGn',
    color_continuous_midpoint=50,
    color='Women (%)',
    width=1000, 
    height=1000,
    maxdepth=3,
)
fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

# Build app with dash
app = dash.Dash()
app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('Percentage of women per occupation (US 2020)', className="app-header--title")
        ]
    ),
    html.Br(),
    dcc.Link(href="https://www.bls.gov/cps/cpsaat11.htm", title="US Bureau"),
    html.Div('* Unspecified values (-) replaced with 50%'),
    dcc.Graph(figure=fig)
])


if __name__ == '__main__':
    app.run_server(debug=True)