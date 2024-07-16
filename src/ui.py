import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import boto3
import datetime

app = dash.Dash(__name__)

# AWS S3 Configuration
s3 = boto3.client('s3')
env_buckets = {
    'QA': {
        'ack': 'gdg0-q-adapter-global-disbursements',
        'psr': 'gdg0-q-bulk-global-disbursements'
    },
    'IST': {
        'ack': 'gdg0-u-adapter-global-disbursements',
        'psr': 'gdg0-u-bulk-global-disbursements'
    }
}

def list_files(bucket_name, prefix=''):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files

def search_files(bucket_name, search_term):
    files = list_files(bucket_name)
    return [file for file in files if search_term in file]

app.layout = html.Div([
    html.H1('S3 File Viewer'),

    dcc.Dropdown(
        id='env-dropdown',
        options=[{'label': env, 'value': env} for env in env_buckets.keys()],
        placeholder='Select Environment',
    ),

    dcc.Dropdown(
        id='bucket-dropdown',
        placeholder='Select Bucket'
    ),

    dcc.Dropdown(
        id='type-dropdown',
        options=[
            {'label': 'ACK', 'value': 'ACK'},
            {'label': 'EOD', 'value': 'EOD'},
            {'label': 'PSR', 'value': 'PSR'},
            {'label': 'GDPost', 'value': 'GDPost'}
        ],
        placeholder='Select Type'
    ),

    html.Div(id='input-container'),

    html.Button('Search', id='search-button'),

    html.Div(id='file-links'),

    dcc.Interval(
        id='interval-component',
        interval=15*60*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('bucket-dropdown', 'options'),
    [Input('env-dropdown', 'value')]
)
def set_bucket_options(selected_env):
    if selected_env:
        buckets = env_buckets[selected_env]
        options = [{'label': name, 'value': value} for name, value in buckets.items()]
        return options
    return []

@app.callback(
    Output('input-container', 'children'),
    [Input('type-dropdown', 'value')]
)
def set_input_box(selected_type):
    if selected_type == 'PSR':
        return dcc.Input(id='input-box', type='text', placeholder='Enter MSG-id')
    elif selected_type in ['ACK', 'EOD', 'GDPost']:
        return dcc.Input(id='input-box', type='text', placeholder='Enter rail-bulk-id')
    return ''

@app.callback(
    Output('file-links', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('env-dropdown', 'value'), State('bucket-dropdown', 'value'), State('type-dropdown', 'value'), State('input-box', 'value')]
)
def update_output(n_clicks, selected_env, selected_bucket, selected_type, input_value):
    if n_clicks is None or not all([selected_env, selected_bucket, selected_type, input_value]):
        return ''

    bucket_name = env_buckets[selected_env]['ack' if selected_type != 'PSR' else 'psr']
    files = search_files(bucket_name, input_value)

    links = [html.A(file, href=f'https://{bucket_name}.s3.amazonaws.com/{file}', target='_blank') for file in files]
    return html.Ul([html.Li(link) for link in links])

if __name__ == '__main__':
    app.run_server(debug=True)
