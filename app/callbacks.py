from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px

from app import app
from viz import analysis, plot_category, description_table,\
    top_categorical_table, wordcloud_to_plotly, crosstab


@app.callback(
    Output('category', 'children'),
    Input('category-name', 'value'))
def choose_category(category_name):
    analysis.update_category(category_name)
    if category_name == 'Не выбрано':
        return html.Div([])
    else:
        return plot_category()


@app.callback(
    Output('description-table', 'children'),
    Input('description-type', 'value'))
def choose_desc_table(description_type):
    if description_type == 'Численные признаки':
        return description_table(False)
    else:
        return description_table(True)


@app.callback(
    Output('hist', 'children'),
    Input('hist-dropdown', 'value'))
def choose_hist(field):
    return html.Div(
        dcc.Graph(figure=px.histogram(analysis.df_numerical, x=field))
    )


@app.callback(
    Output('scatter', 'children'),
    Input('scatter-x-dropdown', 'value'),
    Input('scatter-y-dropdown', 'value'))
def choose_scatter(field_x, field_y):
    return html.Div(
        dcc.Graph(figure=px.scatter(analysis.df_numerical, x=field_x, y=field_y))
    )


@app.callback(
    Output('cat-top-table', 'children'),
    Input('cat-top-dropdown', 'value'))
def choose_top_cat_table(field):
    return top_categorical_table(field)


@app.callback(
    Output('wordcloud', 'src'),
    Input('wordcloud-dropdown', 'value'))
def choose_wordcloud(field):
    return wordcloud_to_plotly(field)


@app.callback(
    Output('crosstab', 'children'),
    Input('crosstab-x-dropdown', 'value'),
    Input('crosstab-y-dropdown', 'value'),
    Input('crosstab-n', 'value'))
def choose_crosstab(field_x, field_y, n):
    return crosstab(field_x, field_y, n)
