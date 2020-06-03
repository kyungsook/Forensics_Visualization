from collections import Counter
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout
from plotly import subplots
import pandas as pd
import cufflinks as cf

import DBManager


class Graph:
    def __init__(self, date_from, date_to):
        self.date_from = date_from
        self.date_to = date_to

        db = DBManager.DBManager('./test.db')

        self.regbinRes, self.regdwordRes, self.regexpandszRes, self.regmultiszRes, self.regqwordRes, self.regszRes \
            = db.order_by_date('Hive', self.date_from, self.date_to)
        self.delRes, self.hwpRes, self.pdfRes, self.jpegRes, self.pngRes, self.pptxRes \
            = db.order_by_date('GeneralFile', self.date_from, self.date_to)
        self.chromeRes, self.whaleRes = db.order_by_date('urls', self.date_from, self.date_to)

        self.hive_record = Counter(self.regbinRes) + Counter(self.regdwordRes) + Counter(self.regexpandszRes) \
                           + Counter(self.regmultiszRes) + Counter(self.regqwordRes) + Counter(self.regszRes)
        self.general_record = Counter(self.delRes) + Counter(self.hwpRes) + Counter(self.pdfRes) \
                              + Counter(self.jpegRes) + Counter(self.pngRes) + Counter(self.pptxRes)
        self.url_record = Counter(self.chromeRes) + Counter(self.whaleRes)

    def get_total_key(self):
        total_key_list = list(Counter(self.hive_record) + Counter(self.general_record) + Counter(self.url_record))
        total_key_list.sort()

        return total_key_list

    def get_hive_key(self):
        hive_key_list = list(Counter(self.regbinRes) + Counter(self.regdwordRes) + Counter(self.regexpandszRes) \
                             + Counter(self.regmultiszRes) + Counter(self.regqwordRes) + Counter(self.regszRes))
        hive_key_list.sort()

        return hive_key_list

    def get_general_key(self):
        general_key_list = list(Counter(self.delRes) + Counter(self.hwpRes) + Counter(self.pdfRes) \
                                + Counter(self.jpegRes) + Counter(self.pngRes) + Counter(self.pptxRes))
        general_key_list.sort()

        return general_key_list

    def get_url_key(self):
        url_key_list = list(Counter(self.chromeRes) + Counter(self.whaleRes))
        url_key_list.sort()

        return url_key_list

    def create_list(self, tablename, listname):
        hive_key_list = self.get_hive_key()
        general_key_list = self.get_general_key()
        url_key_list = self.get_url_key()

        value_list = []

        if tablename == 'Hive':
            if listname == 'regbin':
                for i in hive_key_list:
                    if i not in self.regbinRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regbinRes[i])
            elif listname == 'regdword':
                for i in hive_key_list:
                    if i not in self.regdwordRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regdwordRes[i])
            elif listname == 'regexpand':
                for i in hive_key_list:
                    if i not in self.regexpandszRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regexpandszRes[i])
            elif listname == 'regmultisz':
                for i in hive_key_list:
                    if i not in self.regmultiszRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regmultiszRes[i])
            elif listname == 'regqword':
                for i in hive_key_list:
                    if i not in self.regqwordRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regqwordRes[i])
            elif listname == 'regsz':
                for i in hive_key_list:
                    if i not in self.regszRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.regszRes[i])

        elif tablename == 'General':
            if listname == 'del':
                for i in general_key_list:
                    if i not in self.delRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.delRes[i])
            elif listname == 'hwp':
                for i in general_key_list:
                    if i not in self.hwpRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.hwpRes[i])
            elif listname == 'pdf':
                for i in general_key_list:
                    if i not in self.pdfRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.pdfRes[i])
            elif listname == 'jpeg':
                for i in general_key_list:
                    if i not in self.jpegRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.jpegRes[i])
            elif listname == 'png':
                for i in general_key_list:
                    if i not in self.pngRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.pngRes[i])
            elif listname == 'pptx':
                for i in general_key_list:
                    if i not in self.pptxRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.pptxRes[i])

        elif tablename == 'urls':
            if listname == 'chrome':
                for i in url_key_list:
                    if i not in self.chromeRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.chromeRes[i])
            elif listname == 'whale':
                for i in url_key_list:
                    if i not in self.whaleRes.keys():
                        value_list.append(0)
                    else:
                        value_list.append(self.whaleRes[i])

        return value_list

    def draw_graph_html(self, name):
        # layout = go.Layout(title='세 가지 형태의 선 그래프', titlefont=dict(size=25, color='#ED4C67'))
        layout = Layout(title='세 가지 형태의 선 그래프', titlefont=dict(size=25, color='#ED4C67'))


        # total graph
        res = dict(Counter(self.hive_record) + Counter(self.general_record) + Counter(self.url_record))
        result = go.Bar(x=list(res.keys()), y=list(res.values()), name='Total Access')
        fig = plotly.subplots.make_subplots(rows=2, cols=1)
        fig.append_trace(result, 1, 1)

        # selected graph
        graph_dict = {}
        color = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

        if name == 'Hive':
            tmp = 'Hive'

            graph_dict['date'] = self.get_hive_key()
            graph_dict['regbin'] = self.create_list(tmp, 'regbin')
            graph_dict['regdword'] = self.create_list(tmp, 'regdword')
            graph_dict['regexpand'] = self.create_list(tmp, 'regexpand')
            graph_dict['regmultisz'] = self.create_list(tmp, 'regmultisz')
            graph_dict['regqword'] = self.create_list(tmp, 'regqword')
            graph_dict['regsz'] = self.create_list(tmp, 'regsz')
            df = pd.DataFrame(graph_dict)

            record = ['regbin', 'regdword', 'regexpand', 'regmultisz', 'regqword', 'regsz']

            for i in range(0, 6):
                fig1 = df.iplot(kind='line', x='date', y=record[i], asFigure=True, showlegend=False, color=color[i])
                fig.append_trace(fig1['data'][0], 2, 1)

        elif name == 'General':
            tmp = 'General'

            graph_dict['date'] = self.get_general_key()
            graph_dict['deleted file'] = self.create_list(tmp, 'del')
            graph_dict['hwp'] = self.create_list(tmp, 'hwp')
            graph_dict['pdf'] = self.create_list(tmp, 'pdf')
            graph_dict['jpeg'] = self.create_list(tmp, 'jpeg')
            graph_dict['png'] = self.create_list(tmp, 'png')
            graph_dict['pptx'] = self.create_list(tmp, 'pptx')

            df = pd.DataFrame(graph_dict)
            record = ['deleted file', 'hwp', 'pdf', 'jpeg', 'png', 'pptx']

            for i in range(0, 6):
                fig1 = df.iplot(kind='line', x='date', y=record[i], asFigure=True, showlegend=False, color=color[i])
                fig.append_trace(fig1['data'][0], 2, 1)

        elif name == 'urls':
            tmp = 'urls'

            graph_dict['date'] = self.get_url_key()
            graph_dict['chrome'] = self.create_list(tmp, 'chrome')
            graph_dict['whale'] = self.create_list(tmp, 'whale')

            df = pd.DataFrame(graph_dict)
            record = ['chrome', 'whale']

            for i in range(0, 2):
                fig1 = df.iplot(kind='line', x='date', y=record[i], asFigure=True, showlegend=False, color=color[i*4])
                fig.append_trace(fig1['data'][0], 2, 1)

        plotly.offline.plot({"data": fig, "layout": layout},
                            filename="UserRecord.html", auto_open=False)


if __name__ == '__main__':
    date_from = '2020-03-01'
    date_to = '2020-05-31'
    draw = Graph(date_from, date_to)
    draw.get_total_key()
    draw.draw_graph_html('urls')
