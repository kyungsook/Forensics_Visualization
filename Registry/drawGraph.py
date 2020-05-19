import pygal
import datetime
from collections import Counter

import DBManager

class Graph:
    def __init__(self):
        db = DBManager.DBManager('./test.db')
        self.Hive_record = db.order_by_date('Hive', '2020/03/01', '2020/05/01')
        self.General_record = db.order_by_date('GeneralFile', '2020/03/01', '2020/05/01')
        self.Url_record = db.order_by_date('urls', '2020/03/01', '2020/05/01')

    def total_graph(self):
        dot_chart = pygal.Dot(x_label_rotation=90)
        dot_chart.title = 'All User Records'

        res = dict(Counter(self.Hive_record) + Counter(self.General_record) + Counter(self.Url_record))
        # print(res)
        # print(map(lambda d: d[0], res))
        dot_chart.x_labels = list(res.keys())
        dot_chart.add("Records", list(res.values()))
        dot_chart.render_to_png('./chart.png')

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
    draw = Graph()
    draw.draw_graph()
    draw.total_graph()