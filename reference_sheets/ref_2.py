from nicegui import ui
from random import random


class thing:
    random_scale = 100

chart = None  # global reference so we can update later

def create_chart():
    global chart


    chart = ui.echart({
        'xAxis': {'type': 'category', 'data': ['A', 'B', 'C']},
        'yAxis': {'type': 'value'},
        'series': [{'type': 'bar', 'data': [5, 20, 36]}]
    })


def update_data():
    
    new_data = [random()*thing.random_scale, random()*thing.random_scale, random()*thing.random_scale]
    print(new_data)
    chart.options['series'][0]['data'] = new_data 


@ui.page('/')
def home():
    # Call the function to draw the chart initially
    create_chart()
    ui.slider(min=0, max=100, step=1).bind_value(thing, 'random_scale')
    ui.number('Random Scale',on_change=update_data).bind_value(thing, 'random_scale')

    ui.button('Update Data', on_click=update_data)

ui.run()