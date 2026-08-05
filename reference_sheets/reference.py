from nicegui import ui
from random import random
import numpy as np

num_points = 100

class thing:
    the_value = 1

# Function to create ECharts options based on a multiplier
def create_options(multiplier: float):
    x_data = list(range(num_points))
    y_data = [i * multiplier for i in x_data]
    return {
        'title': {'text': f'Multiplier = {multiplier}'},
        'tooltip': {},
        'xAxis': {'type': 'category', 'data': x_data},
        'yAxis': {'type': 'value'},
        'series': [{
            'type': 'line',
            'data': y_data,
            'smooth': True
        }]
    }


# Initial chart
chart_1 = ui.echart(options=create_options(1)).classes('w-full h-64')

# Slider event handler
def on_slider_change(e):
    chart.refresh()
    new_y_data = []
    print(thing.the_value)
    for i in range(num_points):
        new_y_data.append(random())
    chart_1.options['series'][0]['data'] = new_y_data   # Update chart options

# Slider control
slider = ui.slider(min=1, max=10, step=1,on_change=on_slider_change).bind_value_to(thing, 'the_value')


# Refreshable chart function
@ui.refreshable
def chart():
    # Generate some random data for demonstration
    data = [np.random.randint(0, 100) for _ in range(num_points)]
    
    # Create an ECharts chart
    ui.echart({
        'xAxis': {'type': 'category', 'data': list(range(num_points))},
        'yAxis': {'type': 'value'},
        'series': [{
            'data': data,
            'type': 'line',
            'color': '#4CAF50',
            'smooth': True
        }],
        'title': {'text': 'Auto-Refreshing Chart'}
    }).classes('w-full h-64')

# Timer to refresh chart every 2 seconds


# Initial chart render
chart()


ui.run()