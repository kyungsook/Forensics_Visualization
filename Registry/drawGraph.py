import pygal
from collections import Counter
import plotly
import plotly.graph_objs as go
from plotly import subplots
from matplotlib import pyplot as plt
import pandas as pd
import cufflinks as cf

import DBManager

class Graph:
    def __init__(self):
        db = DBManager.DBManager('./test.db')
        date_from = '2020-03-01'
        date_to = '2020-05-01'
        self.hive_record = db.select_record('Hive', date_from, date_to)
        self.general_record = db.select_record('GeneralFile', date_from, date_to)
        self.url_record = db.select_record('urls', date_from, date_to)

    def get_total_key(self):    #hive, general, url 딕셔너리의 key(날짜) 전체를 하나의 list로 만듦
        total_key_list = list(Counter(self.hive_record) + Counter(self.general_record) + Counter(self.url_record))
        total_key_list.sort()   #날짜 순서대로 정렬
        return total_key_list

    def create_list(self, name):    #total_key_list에 맞게끔 hive, general, url 리스트를 새로 생성
        total_key_list = self.get_total_key()
        value_list = []

        if name == 'Hive':
            for i in total_key_list:
                if i not in self.hive_record.keys():    #total_key_list에 있는 key가 hive_record에 없으면
                    value_list.append(0)                #0 추가
                else:
                    value_list.append(self.hive_record[i])  #있으면 값 추가

        elif name == 'General':
            for i in total_key_list:
                if i not in self.general_record.keys():
                    value_list.append(0)
                else:
                    value_list.append(self.general_record[i])

        elif name == 'urls':
            for i in total_key_list:
                if i not in self.url_record.keys():
                    value_list.append(0)
                else:
                    value_list.append(self.url_record[i])

        return value_list

    def total_graph(self):
        dot_chart = pygal.Dot(x_label_rotation=90)
        dot_chart.title = 'All User Records'

        res = dict(Counter(self.hive_record) + Counter(self.general_record) + Counter(self.url_record))

        dot_chart.x_labels = list(res.keys())
        dot_chart.add("Records", list(res.values()))
        dot_chart.render_to_png('./chart.png')

    def draw_graph_html(self):
        res = dict(Counter(self.hive_record) + Counter(self.general_record) + Counter(self.url_record))
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
        color_list = ['red', 'orange', 'blue']
        record = ['hive', 'general', 'urls']

        df = pd.DataFrame(graph_dict)
        fig = plotly.subplots.make_subplots(rows=2, cols=1)
        fig.append_trace(result, 1, 1)

        for i in range(len(record)):
            fig1 = df.iplot(kind='line', x='date', y=record[i], asFigure=True, showlegend=False,
                            color=color_list[i])
            fig.append_trace(fig1['data'][0], 2, 1)

        plotly.offline.plot({"data": fig, "layout": go.Layout(title="User Records")}, filename="../../../../../../Downloads/Registry/Registry/UserRecord.html",
                            auto_open=True)


    """def draw_graph_html_t(self):
        hive = go.Scatter(x=list(self.hive_record.keys()), y=list(self.hive_record.values()), name='hive file', mode = 'lines+markers')
        general = go.Scatter(x=list(self.general_record.keys()), y=list(self.general_record.values()), name='general file', mode = 'lines+markers')
        url = go.Scatter(x=list(self.url_record.keys()), y=list(self.url_record.values()), name = 'Internet History', mode = 'lines+markers')

        fig = plotly.subplots.make_subplots(rows=3, cols=1)
        fig.append_trace(hive, 1, 1)
        fig.append_trace(general, 2, 1)
        fig.append_trace(url, 3, 1)

        plotly.offline.plot(fig, filename='graph.html', auto_open=True)"""


if __name__ == '__main__':
    draw = Graph()
    draw.draw_graph_html()
    #draw.total_graph()
    #draw.create_list('hive')