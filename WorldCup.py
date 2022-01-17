import dash
from dash import dcc
from dash import html
import pandas as pd
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import matplotlib.pyplot as plt
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pyodbc


# connecting to sql server databse
conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "SERVER=LAPTOP-6ISKNUTC;"
    "Database=DemoDB;"
    "Trusted_Connection=yes;"
)
# reading the dataset
df = pd.read_sql("SELECT *  FROM dbo.WorldCups", conn)
# printinh=g first 5 rows of data set
print(df.head())
print(df.head().dtypes)
df["GoalsScored"] = df["GoalsScored"].astype(int)


# ------------------------------------------------------------


# 1. count how many times each country won the world cup
times_won = (
    df.groupby("Winner", as_index=False)["Winner"]
    .agg({"winner count": "count"})
    .sort_values(by=["winner count"], ascending=False)
)
print(times_won)

# 2. select columns to show goals scored by year
goals_scored_by_year = df[["Year", "GoalsScored"]]
print(goals_scored_by_year)
print(goals_scored_by_year.dtypes)

# 3. create filter where winner country was the winner the same as place for tournament
winner_countries_filter = df["Country"] == df["Winner"]
# apply filter to new dataframe name
winner_countries = df[winner_countries_filter]
print(winner_countries)

app = dash.Dash(__name__)
colors = {"background": "#c44141", "background1": "#29e3b4", "text": "#7FDBFF"}


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    "World Cup Statistics Dashboard (1930-2014)",
                    style={"color": "#6ceb85", "textAlign": "center"},
                ),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id="Year-dopdown",
                            options=[
                                #     {"label": x, "value": x} for x in df["Year"].unique()],
                                #     [{"label": "Select all", "value": "all"}]
                                # ,
                                {"label": x, "value": x}
                                for x in df["Year"].unique()
                            ]
                            + [{"label": "Select all", "value": "all"}],
                            value="all",
                            placeholder="Select Year",
                            # style={"background": "#111111", "width": 400,},
                            style={
                                "padding": "0.5rem",
                                # "margin": "0.5rem",
                                # "boxShadow": "#e3e3e3 4px 4px 2px",
                                "border-radius": "10px",
                            },
                            multi=True,
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H3(
                                            "How many times each country won the world cup"
                                        ),
                                        dcc.Graph(id="pie chart", figure="fig1"),
                                    ],
                                    style={
                                        "margin": "1rem",
                                        "display": "inline-block",
                                        "justify-content": "space-between",
                                        "width": 400,
                                        "color": "#6ceb85",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.H3("Number of Goals Scored by Year"),
                                        dcc.Graph(id="bar chart", figure="fig2"),
                                    ],
                                    style={
                                        "margin": "1rem",
                                        "display": "inline-block",
                                        "justify-content": "space-between",
                                        "width": 400,
                                        "color": "#6ceb85"
                                        # "flex-wrap": "wrap",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.H3(
                                            "Winner Country Was the Same Country as Place for Tournament",
                                            style={"color": "#6ceb85"},
                                        ),
                                        dash_table.DataTable(
                                            id="table",
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in winner_countries.columns
                                            ],
                                            data=winner_countries.to_dict("records"),
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            style={"background": "#29a2b9"},
        )
    ]
)


@app.callback(
    Output("pie chart", "figure"), Input("Year-dopdown", "value"),
)
def update_figure(selected_year):
    if selected_year == "all":
        dff = times_won
        fig1 = px.pie(
            dff, values="winner count", labels=dff["Winner"], color="Winner", hole=0.5
        )
        return fig1
    else:
        dff = df[df["Year"].isin(selected_year)]
        dff = (
            dff.groupby("Winner", as_index=False)["Winner"]
            .agg({"winner count": "count"})
            .sort_values(by=["winner count"], ascending=False)
        )
        fig1 = px.pie(
            dff,
            values="winner count",
            labels=times_won["Winner"],
            color="Winner",
            hole=0.5
            # barmode="group",
        )
        return fig1


@app.callback(
    Output("bar chart", "figure"), Input("Year-dopdown", "value"),
)
def update_figure_bar(selected_year):
    if selected_year == "all":
        dff = goals_scored_by_year
        fig2 = px.bar(dff, x="Year", y="GoalsScored")
        return fig2
    else:
        dff_bar = df[df["Year"].isin(selected_year)]
        dff_bar = (
            dff_bar.groupby("Year", as_index=False)["GoalsScored"]
            .agg({"GoalsScored": "sum"})
            .sort_values(by=["GoalsScored"], ascending=False)
        )
        fig2 = px.bar(dff_bar, x="Year", y="GoalsScored")
        return fig2


@app.callback(
    Output("table", "figure"), Input("Year-dopdown", "value"),
)
def update_table(selected_year):
    if selected_year == "all":
        dff = winner_countries
        fig3 = px.table(dff)
        return fig3
    else:
        dff = df[df["Year"].isin(selected_year)]
        dff = (
            dff.groupby("Year", as_index=False)["GoalsScored"]
            .agg({"GoalsScored": "sum"})
            .sort_values(by=["GoalsScored"], ascending=False)
        )
        fig3 = px.bar(dff, x="Year", y="GoalsScored")
        return fig3


if __name__ == "__main__":
    app.run_server(port=8050, host="0.0.0.0")

