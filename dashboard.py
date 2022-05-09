from dash import Dash, dash_table
import pandas as pd

df = pd.read_csv('output.csv')
df = df[['Title','URL','Section','Keywords','Summary','WMD_Distance','Jaccard Index']]  # prune columns for example
with open('../output.csv') as f:
    file_len = sum(1 for line in f)

app = Dash(__name__)

app.layout = dash_table.DataTable(
    data=df.to_dict('records'),
    filter_action='native',
    columns=[{"name": i, "id": i} for i in df.columns],
    style_cell={'textAlign': 'left'},
    style_table={
        'height': 1600,
    },
    page_size=file_len,
    style_data={
        'width': '250px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'whiteSpace': 'normal', 
        'height': 'auto'
    }
)


if __name__ == '__main__':
    app.run_server(debug=True)