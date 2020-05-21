import pygal
import datetime
from collections import Counter
import plotly
import plotly.graph_objs as go
from plotly import subplots
import pandas as pd
import cufflinks as cf
import random

import DBManager

class Graph:
    def __init__(self, date_from, date_to):
        # self.date_from = '2020-03-01'
        # self.date_to = '2020-05-01'
        self.date_from = date_from
        self.date_to = date_to

        db = DBManager.DBManager('./test.db')
        self.Hive_record = db.order_by_date('Hive', self.date_from, self.date_to)
        self.General_record = db.order_by_date('GeneralFile', self.date_from, self.date_to)
        self.Url_record = db.order_by_date('urls', self.date_from, self.date_to)

    def get_total_key(self):
        total_key_list = list(Counter(self.Hive_record) + Counter(self.General_record) + Counter(self.Url_record))
        total_key_list.sort()
        return total_key_list

    def create_list(self, name):
        total_key_list = self.get_total_key()
        value_list = []

        if name == 'Hive':
            for i in total_key_list:
                if i not in self.Hive_record.keys():
                    value_list.append(0)
                else:
                    value_list.append(self.Hive_record[i])

        elif name == 'General':
            for i in total_key_list:
                if i not in self.General_record.keys():
                    value_list.append(0)
                else:
                    value_list.append(self.General_record[i])

        elif name == 'urls':
            for i in total_key_list:
                if i not in self.Url_record.keys():
                    value_list.append(0)
                else:
                    value_list.append(self.Url_record[i])

        return value_list

    def total_graph(self):
        dot_chart = pygal.Dot(x_label_rotation=90)
        dot_chart.title = 'All User Records'

        res = dict(Counter(self.Hive_record) + Counter(self.General_record) + Counter(self.Url_record))
        # print(res)
        # print(map(lambda d: d[0], res))
        dot_chart.x_labels = list(res.keys())
        dot_chart.add("Records", list(res.values()))
        dot_chart.render_to_png('./UserTotalRecord.png')

    def draw_graph_html(self, tableName):
        res = dict(Counter(self.Hive_record) + Counter(self.General_record) + Counter(self.Url_record))
        result = go.Bar(x=list(res.keys()), y=list(res.values()), name='Total Access')

        total_key_list = self.get_total_key()
        hive_value_list = self.create_list('Hive')
        general_value_list = self.create_list('General')
        url_value_list = self.create_list('urls')

        graph_dict = {}
        graph_dict['date'] = total_key_list
        graph_dict['hive'] = hive_value_list
        graph_dict['general'] = general_value_list
        graph_dict['urls'] = url_value_list
        df = pd.DataFrame(graph_dict)

        record = ['hive', 'general', 'urls']
        color = ['red', 'yellow', 'green']

        fig = plotly.subplots.make_subplots(rows=2, cols=1)
        fig.append_trace(result, 1, 1)
        for i in range(0, 3):
            fig1 = df.iplot(kind='line', x='date', y=record[i], asFigure=True, showlegend=False, color=color[i])
            fig.append_trace(fig1['data'][0], 2, 1)

        plotly.offline.plot({"data": fig, "layout": go.Layout(title="User Records")},
                            filename="UserRecord.html", auto_open=False)

    def draw_graph(self):
        date_chart = pygal.Line(x_label_rotation=90)
        date_chart.title = 'Selected Hive Records'
        date_chart.x_labels = list(self.Hive_record.keys())
        date_chart.add("Frequency",  list(self.Hive_record.values()))
        date_chart.render_to_png('hive.png')

        date_chart = pygal.Line(x_label_rotation=90)
        date_chart.title = 'Selected General File Records'
        date_chart.x_labels = list(self.General_record.keys())
        date_chart.add("Frequency", list(self.General_record.values()))
        date_chart.render_to_png('general.png')

        date_chart = pygal.Line(x_label_rotation=90)
        date_chart.title = 'Selected Internet History Records'
        date_chart.x_labels = list(self.Url_record.keys())
        date_chart.add("Frequency", list(self.Url_record.values()))
        date_chart.render_to_png('url.png')

if __name__ == '__main__':
    date_from = '2020-03-31'
    date_to = '2020-05-01'
    draw = Graph(date_from, date_to)
    draw.draw_graph_html('Hive')
    draw.total_graph()