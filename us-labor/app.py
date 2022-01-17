import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import dash
from dash import html, dcc

# Read csv and delete rows without occupation or tree level (1)
df = pd.read_csv("data/cpsaat11.csv", skiprows=6, sep=",", thousands=r',')
df.columns = ["Occupation", "Total", "Women (%)", "White", "Black_or_african_american", "Asian", "Hispanic_or_latino", "Tree_level"]
df.loc[0, "Occupation"] = "Total"
df = df[~df.Occupation.isna()]
df = df[~df.Tree_level.isna()]
df.Tree_level = df.Tree_level.astype(int)
df["Parent"] = "None"
df.reset_index(inplace=True, drop=True)
df.Total = df.Total.astype(int)

# Find parents for all elements
for i, occ in df.iterrows():
    idx_parent = np.argwhere((df.loc[:i, "Tree_level"] == (occ.Tree_level - 1)).values)
    try:
        df.loc[i, "Parent"] = df.loc[idx_parent[-1][0], "Occupation"]
        if occ["Women (%)"] == '–':
            # Replace missing percentages with parent percentage
            df.loc[i, "Women (%)"] = df.loc[idx_parent[-1][0], "Women (%)"]
    except IndexError:
        df.loc[i, "Parent"] = ""

df["Women (%)"] = df["Women (%)"].astype(float)

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
    width=950, 
    height=950,
    maxdepth=3,
    title="Percentage of women per occupation (US 2020)",
)
fig.update_layout(margin=dict(l=0), paper_bgcolor="#ffffff")
fig.add_annotation(
    text="Data obtained from the <a href='https://www.bls.gov/cps/cpsaat11.htm'> U.S. BUREAU OF LABOR STATISTICS </a>.",
    xref="paper", yref="paper",
    x=0.07, y=1.04, showarrow=False
)
fig.add_annotation(
    text="* Unspecified values (-) replaced with parent percentages.",
    xref="paper", yref="paper",
    x=0.07, y=1.02, showarrow=False
)


plotly.offline.plot(
    fig, 
    filename='labor-women.html',
)



# # Build app with dash
# app = dash.Dash()
# app.layout = html.Div([
#     html.Div(
#         className="app-header",
#         children=[
#             html.Div('Percentage of women per occupation (US 2020)', className="app-header--title")
#         ]
#     ),
#     html.Br(),
#     dcc.Link(href="https://www.bls.gov/cps/cpsaat11.htm", title="US Bureau"),
#     html.Div('* Unspecified values (-) replaced with 50%'),
#     dcc.Graph(figure=fig)
# ])


# if __name__ == '__main__':
#     app.run_server(debug=True)
#     server = app.server