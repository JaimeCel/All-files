from dash import Dash, dcc, html,Input, Output
import plotly.express as px
import pandas as pd
spacex_df=pd.read_csv("spacex_launch_dash.csv")




launch_sites = spacex_df['Launch Site'].unique()


dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]


site_dropdown = dcc.Dropdown(
    id='site-dropdown',
    options=dropdown_options,
    value='ALL',  
    placeholder="Select a Launch Site here",
    searchable=True
)
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()


payload_slider = dcc.RangeSlider(
    id='payload-slider',
    min=0,
    max=10000,
    step=1000,
    marks={i: str(i) for i in range(0, 10001, 2000)}, 
    value=[min_payload, max_payload]  
)

app = Dash(__name__)


app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard"),
    site_dropdown, payload_slider,
    dcc.Graph(id='success-pie-chart'),
    dcc.Graph(id='success-payload-scatter-chart')
])
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
       
        df_all = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df_all, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
        return fig
    else:
       
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
       
        success_counts = df_site['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].map({0: 'Failed', 1: 'Success'})
        fig = px.pie(success_counts, values='count', names='class',
                     title=f"Launch Success vs Failure for site {entered_site}")
        return fig
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    df_filtered = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                             (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]

    fig = px.scatter(df_filtered,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title='Payload vs. Success for Selected Site and Range')
    return fig


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)