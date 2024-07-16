import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from urllib.parse import urlparse

app = dash.Dash(__name__)

# Function to download file from S3
def download_file_from_s3(access_key, secret_key, endpoint, file_name, verify_ssl=False):
    parsed_url = urlparse(endpoint)
    host = parsed_url.hostname
    port = parsed_url.port
    path_parts = parsed_url.path.lstrip('/').split('/')
    bucket_name = path_parts[0]  # Assuming the first part is the bucket name
    file_key = '/'.join(path_parts[1:] + [file_name])
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    s3_client = session.client('s3', endpoint_url=f"https://{host}:{port}", verify=verify_ssl)
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        data = response['Body'].read().decode('utf-8')
        return data
    except NoCredentialsError:
        return "Credentials not available"
    except ClientError as e:
        return f"Client error: {e}"

# Initialize the S3 client
def initialize_s3_client(access_key, secret_key, endpoint, verify_ssl=False):
    parsed_url = urlparse(endpoint)
    host = parsed_url.hostname
    port = parsed_url.port
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    s3_client = session.client('s3', endpoint_url=f"https://{host}:{port}", verify=verify_ssl)
    return s3_client

# Function to list files in a bucket
def list_files(s3_client, bucket_name):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return files
    except ClientError as e:
        return []

# Function to search files containing a specific term
def search_files(s3_client, bucket_name, search_term):
    files = list_files(s3_client, bucket_name)
    return [file for file in files if search_term in file]

# Define environment buckets
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

# Define the Dash app layout
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

# Update bucket options based on selected environment
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

# Update input box based on selected type
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

# Display search results
@app.callback(
    Output('file-links', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('env-dropdown', 'value'), State('bucket-dropdown', 'value'), State('type-dropdown', 'value'), State('input-box', 'value')]
)
def update_output(n_clicks, selected_env, selected_bucket, selected_type, input_value):
    if n_clicks is None or not all([selected_env, selected_bucket, selected_type, input_value]):
        return ''

    # Initialize S3 client
    access_key = 'your-access-key'
    secret_key = 'your-secret-key'
    endpoint = 'your-endpoint'
    s3_client = initialize_s3_client(access_key, secret_key, endpoint)

    files = search_files(s3_client, selected_bucket, input_value)

    links = [html.A(file, href=f'https://{selected_bucket}.s3.amazonaws.com/{file}', target='_blank') for file in files]
    return html.Ul([html.Li(link) for link in links])

if __name__ == '__main__':
    app.run_server(debug=True)
