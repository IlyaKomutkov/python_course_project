import numpy as np
import pandas as pd
from dash import dcc
from dash import html
from dash import dash_table
import io
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import plotly.express as px

from analysis import Analysis

analysis = Analysis()


def create_layout():
    sections = ['Не выбрано', 'Аминокислоты', 'Протеины', 'Энергия']

    return html.Div([
        html.Div(html.H1(children='Анализ спортивного питания'),
                 style={'text-align': 'center'}),
        html.Div(dcc.Markdown(children='Выберите тип спортивного питания:', style={'font-size': '24px'}),
                 style={'width': '29%', 'display': 'inline-block'}),
        html.Div(dcc.Dropdown(
            id='category-name',
            options=[{'label': x, 'value': x} for x in sections],
            value='Не выбрано'),
            style={'width': '69%', 'display': 'inline-block',
                   'float': 'right',
                   'margin-top': '20px'}),
        html.Div(id='category', style={'margin': '30px'})])


def description_table(is_categorical):
    if is_categorical:
        desc_table = analysis.df.describe(include='object').reset_index()  # сделать выбор только числа?
    else:
        desc_table = analysis.df.describe().reset_index()
    desc_table.rename(columns={'index': 'metric'}, inplace=True)
    return dash_table.DataTable(
        data=desc_table.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in desc_table.columns]
    )


def corr_heatmap():
    corr = analysis.df_numerical.corr().round(3)
    mask = np.zeros_like(corr, dtype=bool)
    mask[np.triu_indices_from(mask)] = True
    df_corr_triangle = corr.mask(mask).dropna(how='all')
    fig = px.imshow(df_corr_triangle, text_auto=True, color_continuous_scale='RdBu_r')
    return html.Div([
        html.H3('Матрица корреляций'),
        dcc.Graph(figure=fig)
    ])


def top_categorical_table(field):
    table = analysis.dict_counts[field].head(10)
    return dash_table.DataTable(
        data=table.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in table.columns]
    )


def wordcloud_to_plotly(field):
    frequencies = analysis.dict_counts[field]['count'].to_dict()
    wc = WordCloud(background_color="white").generate_from_frequencies(frequencies)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    buf = io.BytesIO()
    plt.savefig(buf, format="png")  # save to the above file object
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
    buf.close()
    return "data:image/png;base64,{}".format(data)


def crosstab(field_x, field_y, n):
    values_x = analysis.dict_counts[field_x].head(n).index
    values_y = analysis.dict_counts[field_y].head(n).index
    df = analysis.df[analysis.df[field_x].isin(values_x) & analysis.df[field_y].isin(values_y)]
    crosstab_table = pd.crosstab(df[field_x], df[field_y]).reset_index()
    crosstab_table.rename(columns={crosstab_table.columns[0]: ''}, inplace=True)
    return dash_table.DataTable(
        data=crosstab_table.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in crosstab_table.columns]
    )


def plot_category():
    return html.Div([
        html.H3('Таблица описательных статистик'),

        dcc.RadioItems(id='description-type',
                       options=['Численные признаки', 'Категориальные признаки'],
                       value='Численные признаки'),
        html.Div(id='description-table'),

        html.Div(html.H2(children='Анализ численных полей'),
                 style={'text-align': 'center'}),

        html.H3('Гистограмма'),
        dcc.Dropdown(analysis.df_numerical.columns, 'price', id='hist-dropdown'),
        html.Div(id='hist'),

        html.H3('График рассеяния'),
        html.Div([
            html.Div(dcc.Markdown(children='Ось Y:', style={'font-size': '24px'}),
                     style={'width': '10%', 'display': 'inline-block'}),
            html.Div(dcc.Dropdown(analysis.df_numerical.columns, 'price', id='scatter-y-dropdown'),
                     style={'width': '34%', 'display': 'inline-block'}),
            html.Div(dcc.Markdown(children='Ось X:', style={'font-size': '24px'}),
                     style={'width': '10%', 'display': 'inline-block',
                            'margin-left': '20px'}),
            html.Div(dcc.Dropdown(analysis.df_numerical.columns, 'Вес нетто, г', id='scatter-x-dropdown'),
                     style={'width': '34%', 'display': 'inline-block'}),
        ]),
        html.Div(id='scatter'),

        corr_heatmap(),

        html.Div(html.H2(children='Анализ текстовых полей'),
                 style={'text-align': 'center'}),

        dcc.Markdown(f'''Поля с множественными значениями 
        (через запятую): {", ".join(analysis.df_categorical_comma_fields)}'''),

        dcc.Markdown(f'''Поля без множественных значений: 
            {", ".join(analysis.df_categorical_no_comma_fields)}'''),

        html.H3(f'Топ 10 часто встречающихся значений  в поле'),
        dcc.Dropdown(analysis.df_categorical.columns, 'Цель', id='cat-top-dropdown'),
        html.Div(id='cat-top-table'),

        html.H3(f'Облако слов'),
        dcc.Dropdown(analysis.df_categorical.columns, 'Цель', id='wordcloud-dropdown'),
        html.Img(id='wordcloud', style={'text-align': 'center'}),

        html.H3(f'Таблица сопряженности'),
        html.Div([
            html.Div(dcc.Markdown(children='Строки:', style={'font-size': '24px'}),
                     style={'width': '10%', 'display': 'inline-block'}),
            html.Div(dcc.Dropdown(analysis.df_categorical.columns, 'Цель', id='crosstab-x-dropdown'),
                     style={'width': '34%', 'display': 'inline-block'}),
            html.Div(dcc.Markdown(children='Столбцы:', style={'font-size': '24px'}),
                     style={'width': '10%', 'display': 'inline-block',
                            'margin-left': '20px'}),
            html.Div(dcc.Dropdown(analysis.df_categorical.columns, 'Страна производитель', id='crosstab-y-dropdown'),
                     style={'width': '34%', 'display': 'inline-block'}),
        ]),
        html.Div([
            html.Div(dcc.Markdown(children='Количество самых частых значений для матрицы сопряженности',
                                  style={'font-size': '20px'}),
                     style={'width': '49%', 'display': 'inline-block'}),
            html.Div(dcc.RadioItems(id='crosstab-n',
                                    options=[5, 10, 15],
                                    value=5),
                     style={'width': '49%', 'display': 'inline-block'})
        ]),
        html.Div(id='crosstab')
    ])


layout = create_layout()
