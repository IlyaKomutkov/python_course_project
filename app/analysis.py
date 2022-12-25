import pandas as pd
from collections import Counter


class Analysis:
    def __init__(self):
        self.current_category = None
        self.df = None
        self.df_numerical = None
        self.df_categorical = None
        self.df_categorical_comma_fields = None
        self.df_categorical_no_comma_fields = None
        self.dict_counts = None

        self.all_dicts = {'Аминокислоты': {'df': pd.read_csv('acids.csv')},
                          'Протеины': {'df': pd.read_csv('proteins.csv')},
                          'Энергия': {'df': pd.read_csv('energy.csv')},
                          'Не выбрано': {}}
        self.preprocess_data()

    def preprocess_data(self):
        for key, value in self.all_dicts.items():
            if key != 'Не выбрано':
                new_dict = self.all_dicts[key]
                df = value['df']
                na_ratio = df.isna().sum() / df.shape[0]
                columns_to_drop = list(na_ratio[na_ratio > 0.9].index)
                df.drop(columns=columns_to_drop, inplace=True)  # drop columns with many nans

                numerical = df.select_dtypes(include=['float64', 'int64'])
                categorical = df.select_dtypes(include=['object'])

                comma = []
                no_comma = []
                dict_counts = dict()
                for column in categorical.columns:
                    if any(categorical[column].dropna().str.contains(', ')) and column != 'name':
                        comma.append(column)
                        all_vals = []
                        for val in categorical[column].dropna().values:
                            all_vals.extend(val.split(', '))
                    else:
                        no_comma.append(column)
                        all_vals = categorical[column].dropna().values
                    cnt = pd.Series(Counter(all_vals))
                    count_df = pd.DataFrame({'value': cnt.index, 'count': cnt, 'ratio': cnt})
                    count_df['ratio'] = count_df['ratio'] / categorical.shape[0]
                    count_df.sort_values('count', ascending=False, inplace=True)
                    dict_counts[column] = count_df
                new_dict['df'] = df
                new_dict['df_numerical'] = numerical
                new_dict['df_categorical'] = categorical
                new_dict['df_categorical_comma_fields'] = comma
                new_dict['df_categorical_no_comma_fields'] = no_comma
                new_dict['dict_counts'] = dict_counts
                self.all_dicts[key] = new_dict

    def update_category(self, category):
        self.current_category = category
        current_dict = self.all_dicts[category]
        if category != 'Не выбрано':
            self.df = current_dict['df']
            self.df_numerical = current_dict['df_numerical']
            self.df_categorical = current_dict['df_categorical']
            self.df_categorical_comma_fields = current_dict['df_categorical_comma_fields']
            self.df_categorical_no_comma_fields = current_dict['df_categorical_no_comma_fields']
            self.dict_counts = current_dict['dict_counts']

