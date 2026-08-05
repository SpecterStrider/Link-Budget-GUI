# Link Budget & Margin Sim

from Node import * 
from Plot import Plot
from Link import Link
from Environment import Environment
from Losses.thermal import thermal_noise_floor

from nicegui import ui
import math

## ====================================================


# global reference 
live_plot = None

default_config      = Config()
default_link_env    = Environment()
default_node        = Node(default_config)
default_link        = Link(default_node, default_node, default_link_env)
plot                = Plot()



## =====================================================================

def freq_sweep(link:Link, start_freq:float, stop_freq:float, distance:float) -> tuple[list[float],list[float],list[float]]:
    """
    Frequency sweeping the link budget and SNR 

    Parameters:
        link      (Link): configured link that is to be swept 
        start_freq (GHz): sweep starting frequency 
        stop_freq  (GHz): sweep stoppping frequency
        distance    (km): sweep distance

    Returns:
        tuple ([ x_axis, P_rx, snr] ) : 
        x_axis  (GHz): frequency range values \n
        P_rx    (dBm): power recieved \n
        snr     (dB): snr
    """
    
    # Init return list
    x_axis = []
    P_rx   = []
    snr    = []

    # Sweep conditions
    num_steps       = 250
    freq_step       = (stop_freq - start_freq) / num_steps    # units of GHz / step
    link.distance   = distance

    for i in range(0,num_steps + 1):
        # Stepping frequency
        link.freq_GHz = plot.start_freq + ((i) * freq_step)

        x_axis.append(link.freq_GHz)
        
        P_rx.append(link.link_budget())
        snr.append(link.link_SNR())

    return x_axis, P_rx, snr



def dist_sweep(link:Link, freq:float, stop_dist:float) -> tuple[list[float], list[float], list[float]]: 
    """
    Distance sweeping link for power recived and SNR

    Parameters:
        link (Link): configured link that is to be swept
        freq (GHz) : frequency of sweep
        stop_dist(km): length of distance sweep

    Returns:
        tuple ([ x_axis: list, P_rx: list ]): 
        x_axis  (km): list of x axis values \n
        P_rx    (dBm): list of power recieved \n
        snr     (dB): list of SNR
    """

    # Init return list
    x_axis = []
    P_rx   = []
    snr    = []

    # Sweep conditons
    link.freq_GHz = freq
    num_steps = 250
    step_dist = stop_dist / num_steps

    for i in range(1,num_steps+1):
        i_step_distance = i * step_dist
        link.distance   = i_step_distance

        x_axis.append(i_step_distance)        
        P_rx.append(link.link_budget())
        snr.append(link.link_SNR())
    
    return x_axis, P_rx, snr



def create_live_plot():
    ''' Generates live plot for UI '''

    global live_plot

    live_plot = ui.echart({
    'tooltip': {
        'trigger': 'axis',
        'formatter': 'Error : Unset'
    },   
    'xAxis': {
        'type': 'category',
        'data': [],
        'name': "Error : Unset",
        'nameLocation': 'middle',
        'nameGap': 35,
        'axisLabel': {
            'interval': 9,
            'showMinLabel': True,
            'showMaxLabel': True,
            'hideOverlap': True,
            'show': 'true', # ensure labels are visible
            'overflow': 'truncate',
            'align': 'center' # align label text
        },
    },
    'yAxis': {
        'type': 'value',
        'data': [],
        'name':'Error : Unset',
        'nameLocation': 'middle',
        'nameGap': 35,
        'axisLabel': {
            'show': 'true'
        }
    },    
    'series': [
        {'type': 'line',
         'name':'Error : Unset',
         'smooth':True,
         'data': [],
         'showSymbol': False,},
         {'type': 'line',
         'name':'Noise Floor',
         'smooth':True,
         'data': [],
         'showSymbol': False,},
        ]
    }).classes('w-full h-full')

    



def update_live_plot(e: ui.echart):
    ''' Updates plot '''

    # Init plot update variables 
    x_axis = [] 
    y_axis = []
    
    x_title = "Error : Unset"
    y_title = "Error : Unset"
    data_name = "Unset"
    tooltip_str = ''


    # update tempature units and humidity
    default_link.env.update()
    
    # Init sweep vars
    default_node      = Node(default_config)
    default_link.N_tx = default_node
    default_link.N_rx = default_node

    # Sweep Type
    if plot.sweep_type == "frequency":
        plot._is_dist_sweep = False
        plot._is_freq_sweep = True
        tooltip_str         = 'Frequency : {b0} GHz <br />'
        x_axis, P_rx, snr   = freq_sweep(default_link, plot.start_freq, plot.stop_freq, plot.freq_sweep_distance)
        x_title             = "Frequency (GHz)"
    
    elif plot.sweep_type == "distance":
        plot._is_dist_sweep = True
        plot._is_freq_sweep = False
        tooltip_str         = 'Distance : {b0} km <br />'
        x_axis, P_rx, snr   = dist_sweep(default_link, plot.dist_sweep_frequency, plot.stop_distance)
        x_title             = "Distance (km)"


    # Plot Type
    if plot.plot_type == "Link Budget":
        # Sweep Link Budget
        y_axis      = P_rx 
        y_title     = "Power Recived (dBm)"
        data_name   = "P_rx"
        tooltip_str += 'P_rx : {c0} dBm'

    elif plot.plot_type == 'SNR plot':
        # sweep SNR
        y_axis      = snr
        y_title     = "SNR (dB)"
        data_name   = "SNR Plot"
        tooltip_str += 'SNR : {c0} dB'


    noise_floor = []

    if plot.plot_noise_floor and (plot.plot_type == "Link Budget"):
        y_axis = [max(num,default_link.noise_floor) for num in y_axis]
        noise_floor = [default_link.noise_floor] * len(x_axis)

    if plot.plot_noise_floor and (plot.plot_type == "SNR plot"):
        y_axis = [max(num,0) for num in y_axis]
        

    # format plot data to be pretty
    y_axis = [round(num, 2) for num in y_axis]
    x_axis = [round(num, 2) for num in x_axis]
    
    # Update Plot
    live_plot.options['xAxis']['data'] = x_axis
    live_plot.options['xAxis']['name'] = x_title
    live_plot.options['yAxis']['name'] = y_title

    live_plot.options['series'][0]['data'] = y_axis 
    live_plot.options['series'][0]['name'] = data_name

    live_plot.options['series'][1]['data'] = noise_floor

    live_plot.options['tooltip']['formatter'] = tooltip_str

                        

def set_sweep_type(p_type:str):
    '''
    Helper func for setting plot in UI
    
    Parameters:
        p_type (str):  plot type ("frequency" or "distance") 
    '''
    plot.sweep_type = p_type
    update_live_plot(None)


    


## =====================================================================



@ui.page('/')
def home():
    ui.page_title('Link Budget')
    ui.query('body').style('background-color: #bebebeff')

    with ui.column(align_items='center').style('width:98vw; height:90vh; padding: 0px;'):

        with ui.row(align_items='center').style('height: 100%'):

        
            ## Plot Card
            with ui.card().style('border-radius: 20px; padding: 20px; width: 35vw; height: 60vh;\
                                    background: white; display: flex; flex-direction: column'):
                
                with ui.column().classes('w-full items-center justify-center h-full'):
                    with ui.carousel(animated=True, arrows=True, on_value_change=update_live_plot).style('width: 25vw; height : 10vh;').props("control-color=black") as carousel:

                        # Link Budget
                        with ui.carousel_slide('Link Budget'):

                            with ui.column().classes('w-full items-center justify-center h-full'):
                                ui.label('Link Budget').style('font-weight: bold; font-size: 24px;')

                        # SNR
                        with ui.carousel_slide('SNR plot'):

                            with ui.column().classes('w-full items-center justify-center h-full'):
                                ui.label("SNR").style('font-weight: bold; font-size: 24px')

                    carousel.bind_value(plot, 'plot_type')
                    
                    create_live_plot()

                    with ui.row(wrap=False, align_items='start').style('width: 100%;'):
                        with ui.dropdown_button(auto_close=True, split=True, on_click=update_live_plot).bind_text(plot, 'sweep_type').style('font-weight: bold; font-size: 14px; width:150px'):
                            ui.item('Frequency' , on_click=lambda : set_sweep_type("frequency"))
                            ui.item('Distance'  , on_click=lambda : set_sweep_type("distance")) 

                        ui.number(label='Frequency (GHz)',  precision=0,on_change=update_live_plot).bind_value(plot, 'dist_sweep_frequency').bind_visibility(plot, '_is_dist_sweep').style('width: 7vw;')
                        ui.number(label='Stop Distance (km)',  precision=1, on_change=update_live_plot).bind_value(plot, 'stop_distance').bind_visibility(plot, '_is_dist_sweep').style('width: 7vw;')

                        ui.number(label='Distance (km)',  precision=2, on_change=update_live_plot).bind_value(plot, 'freq_sweep_distance').bind_visibility(plot, '_is_freq_sweep').style('width: 7vw;')
                        ui.number(label='Start Freq (GHz)',  precision=0, on_change=update_live_plot).bind_value(plot, 'start_freq').bind_visibility(plot, '_is_freq_sweep').style('width: 7vw;')
                        ui.number(label='Stop Freq (GHz)',  precision=0, on_change=update_live_plot).bind_value(plot, 'stop_freq').bind_visibility(plot, '_is_freq_sweep').style('width: 7vw;')
                


            ## Settings and Numbers card
            with ui.card().style('border-radius: 20px;  width: 50vw; height: 75vh; ' \
                                'background: white; display: flex; flex-direction: column; padding: 0;' \
                                'overflow: hidden;'):
                
                with ui.row():    
                    with ui.tabs() as tabs:
                        ui.tab('Config')
                        ui.tab('Environment')
                        ui.tab('About')
                    
                ui.separator()

                with ui.tab_panels(tabs, value='Config').style('flex: 1; width: 100%; height: 100%; background-color: #b4d6d6;'):


                    with ui.tab_panel('Config').style('flex: 1; width: 100%; height: 100%;'):

                        with ui.column().classes('w-full items-center justify-start'):
                        
                            with ui.card().style('flex: 1; width: 100%; height: 100%; padding: 20'):
                                with ui.row().style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                    with ui.column().style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                        ui.label('Transmitter').style('font-weight: bold; font-size: 18px')
                                        with ui.column(wrap=False, align_items='start').style('flex: 1; width: 100%; height: 100%;'):   
                                            ui.number(label='Gain (dB)', precision=4, on_change=update_live_plot).bind_value(default_config, 'G_tx').classes('w-1/3')
                                            
                                            ui.number(label='Loss (dB)',  precision=4,on_change=update_live_plot).bind_value(default_config, 'L_tx').classes('w-1/3')

                                            with ui.row(wrap=False,align_items='center').classes('w-2/3'):
                                                ui.number(label='TX Power (dBm)', precision=4,on_change=update_live_plot).bind_value(default_config, 'P_tx').classes('w-1/2')
                                                ui.label().bind_text_from(default_config, 'P_tx', backward=lambda v:f'Watt :\t {((10 ** (v / 10)) / 1000):.3g} W').style('color:grey')                                            

                                    with ui.column().style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                        ui.label('Receiver').style('font-weight: bold; font-size: 18px')
                                        with ui.column(wrap=False, align_items='start').style('flex: 1; width: 100%; height: 100%;'):   
                                            ui.number(label='Gain (dB)',  precision=0, on_change=update_live_plot).bind_value(default_config, 'G_rx').classes('w-1/3')
                                            
                                            ui.number(label='Loss (dB)',  precision=0, on_change=update_live_plot).bind_value(default_config, 'L_rx').classes('w-1/3')
                                            
                                            ui.number(label='Noise (dBm)', precision=0, on_change=update_live_plot).disable().bind_value(default_config, 'noise').classes('w-1/3')
                                            
                                            


                            with ui.card().style('flex: 1; width: 100%; height: 100%; padding: 20'):
                                with ui.column().style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                    ui.label('Link').style('font-weight: bold; font-size: 18px')
                                    with ui.column(wrap=False, align_items='start').style('flex: 1; width: 100%; height: 100%;'):
                                            with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):   
                                                ui.number(label='Bandwidth (MHz)', precision=4,on_change=update_live_plot).bind_value(default_link, 'bandwidth').classes('w-1/4')
                                                check = ui.checkbox().bind_value(plot, 'plot_noise_floor').on_value_change(update_live_plot)
                                                check.bind_text_from(default_link, 'noise_floor', backward=lambda v:f'Plot Noise floor:\t {v:.2f} dBm')
                                                
                                                
                                            with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):   
                                                ui.number(label='Polarization Tilt (degrees)',  format='%0.1f').bind_value(default_link, 'polar_tilt').classes('w-1/4')
                                                ui.slider(min=-90, max=90, step=0.1,on_change=update_live_plot).bind_value(default_link, 'polar_tilt').classes('w-5/7')
                                                
                                            with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):
                                                ui.number(label='Elevation Angle (degree)', format='%0.1f').bind_value(default_link, 'elev_angle').classes('w-1/4')
                                                ui.slider(min=-90, max=90, step=0.1,on_change=update_live_plot).bind_value(default_link, 'elev_angle').classes('w-5/7')
                                                
                            ui.space()



                    with ui.tab_panel('Environment').style('flex: 1; width: 100%; height: 100%;'):

                        with ui.column().classes('w-full items-center justify-start'):

                            with ui.card().style('flex: 1; width: 100%; height: 100%; padding: 20'):
                                
                                switch_atmo = ui.switch("Atmosphere",on_change=update_live_plot).bind_value(default_link.env, '_is_atmo')

                                with ui.column().bind_visibility(switch_atmo, 'value').style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):   
                                        ui.number(label='Humidity (%)',format='%.2f').bind_value(default_link.env, 'humidity')
                                        ui.slider(min=0, max=1,step=0.01,on_change=update_live_plot).bind_value(default_link.env, 'humidity')

                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):   
                                        ui.number(label='Temp (C)',format='%.1f').bind_value(default_link.env, 'temp_C')
                                        ui.slider(min=0, max=100,on_change=update_live_plot).bind_value(default_link.env, 'temp_C')
                                        
                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):
                                        ui.number(label='Pressure (kPa)',  format='%.1f').bind_value(default_link.env, 'pressure_kPa')
                                        ui.slider(min=0, max=120 , step=0.1, on_change=update_live_plot).bind_value(default_link.env, 'pressure_kPa')
                                        
                                    
                                    
                                    
                                
                                

                            with ui.card().style('flex: 1; width: 100%; height: 100%; padding: 20'):

                                switch_cloud = ui.switch("Clouds",on_change=update_live_plot).bind_value(default_link.env, '_is_cloudy')

                                with ui.column().bind_visibility(switch_cloud, 'value').style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):   
                                        ui.number(label='Temp (C)',  format='%.1f').bind_value(default_link.env, 'cloud_temp_C')
                                        ui.slider(min=0, max=100,on_change=update_live_plot).bind_value(default_link.env, 'cloud_temp_C')
                                        

                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):
                                        ui.number(label='Density (g/m^3)',  format='%.2f').bind_value(default_link.env, 'cloud_density')
                                        ui.slider(min=0, max=25, step=0.01,on_change=update_live_plot).bind_value(default_link.env, 'cloud_density')
                                        
                                
                            with ui.card().style('flex: 1; width: 100%; height: 100%; padding: 20'):

                                switch_rain = ui.switch("Rain",on_change=update_live_plot).bind_value(default_link.env, '_is_raining')

                                with ui.column().style('flex: 1; width: 100%; height: 100%; padding: 0').bind_visibility(switch_rain, 'value'):

                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):
                                        ui.number(label='Rate (mm/hr)',format='%.1f', on_change=update_live_plot).bind_value(default_link.env, 'rainrate')                    
                                        ui.slider(min=0, max=50, step=0.1,on_change=update_live_plot).bind_value(default_link.env, 'rainrate')
                                        
                                    with ui.row(wrap=False, align_items='center').style('flex: 1; width: 100%; height: 100%;'):
                                        ui.number(label='Path Coverage (%)', format='%.2f').bind_value(default_link.env, 'rain_path_per')
                                        ui.slider(min=0, max=1, step=0.01,on_change=update_live_plot).bind_value(default_link.env, 'rain_path_per')
                                        
                                
                            ui.space()
                               

                    with ui.tab_panel('About').style('flex: 1; width: 100%; height: 100%;'):

                        with ui.column().classes('w-full items-center justify-start'):

                            with ui.card().style('flex: 1; width: 40%; height: 100%; padding: 20'):
                                with ui.column(align_items='center').style('flex: 1; width: 100%; padding: 0'):
                                    ui.label("Model only valid on 1 GHz - 1,000 GHz ").style('font-weight: bold;')

                            with ui.card().style('flex: 1; width: 40%; height: 100%; padding: 20'):
                                with ui.column(align_items='center').style('flex: 1; width: 100%; height: 100%; padding: 0'):
                                    ui.label("Model Assumptions: ").style('font-weight: bold;')
                                    with ui.column(align_items='start'):
                                        ui.label("- Flat world ")
                                        ui.label("- Uniform Rainfall ")
                                        ui.label("- Uniform Atmospheric Pressure Density")
                                        ui.label("- Uniform Tempature")
                                        ui.label("- Narrowband Signal Approximation")
                                                                    
                            with ui.card().style('flex: 1; width: 40%; height: 100%; padding: 20'):
                                with ui.column(align_items='center').style('flex: 1; width: 100%; padding: 0'):
                                    ui.label("Cloud attenuation is only valid up to 200 GHz").style('font-weight: bold;')

ui.run()
