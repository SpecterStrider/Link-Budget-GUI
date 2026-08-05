from nicegui import ui


class Demo:
    def __init__(self):
        self.slide_state = '1'
        self.number = 1

demo = Demo()

def check_yo_self(e):
    if v.value == False:
        demo.number = int(demo.slide_state)
    print(demo.slide_state)


with ui.carousel(arrows=True, on_value_change=check_yo_self).props("control-color=black").style('width:30vw; height:30vh;') as carousel:
    with ui.carousel_slide('1'):
        ui.label('First slide content')
    with ui.carousel_slide('2'):
        ui.label('Second slide content')
    with ui.carousel_slide('3'):
        ui.label('Third slide content')


carousel.bind_value(demo, 'slide_state')

ui.label().bind_text_from(carousel, 'value')

v = ui.checkbox('visible', value=True)
ui.number(label="noise floor (dBm)" , value=-174,).bind_enabled(v,'value')
print(v.value)

ui.run()