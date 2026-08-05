# Rainfall attenuation model
#
# ONLY VALID for 1 - 1,000 GHz
#
# designed using
# ITU-R P.383-3, ITU-R P.387-8, ITU-R P.530-17 and MATLAB rainpl().m

import matplotlib.pyplot as plt
import math


def rain_pl(dist:float, freq:float, rainrate:float, elev:float = 0, tau:float = 0) -> float:
    '''
    Calculates path loss due to rain

    Parameters:
        dist      (km)  : path distance
        freq      (GHz) : path frequency
        rainrate (mm/hr): how fast / hard is it rainning
        elev (degree)   : elevation angle of path
        tau (degree)    : polarization tilt angle 

    Returns:
        total attenuation (dB) : total path loss due to rain
    '''

    # specific attenuation
    gamma, coefficents = specific_attenuation(rainrate,freq, elev, tau)
    a = coefficents[3]

    # path reduction scale factor 
    # rainfall is spacially cellular (non-uniform) along the path
    # 
    # term_1 = 0.477 * (dist ** 0.633)
    # term_2 = rainrate ** (0.073 * a)
    # term_3 = freq ** 0.123         
    # term_4 = 10.579 * (1 - math.exp(-0.024 * dist))
    # r = 1 / (term_1 * term_2 * term_3 - term_4)
    
    # but if rainfall is unform along path
    r = 1
    
    # effective dist 
    d_eff = dist * r

    total_attenuation = d_eff * gamma

    return total_attenuation



def specific_attenuation(rainrate:float, freq:float, elev:float, tau:float) -> float:
    '''
    Calculates **specific** loss due to rain

    Parameters:
        freq      (GHz) : path frequency
        rainrate (mm/hr): how fast / hard is it rainning
        elev (degree)   : elevation angle of path in range [-90,90]
        tau (degree)    : polarization tilt angle in range [-90,90]
    
    Returns:
        gamma (dB / km) : specific rain loss
    '''

    # k_H =========================================
    a_j = [-5.3398, -0.35351,-0.23789,-0.94158]
    b_j = [-0.10008, 1.26970, 0.86036, 0.64552]
    c_j = [ 1.13098, 0.45400, 0.15354, 0.16817]
    m = -0.18961
    c =  0.71147

    # horizontal K component
    k_H = k_compenet(freq, a_j, b_j, c_j, m, c)    

    # k_V =========================================
    a_j = [-3.80595, -3.44965,-0.39902, 0.50167]
    b_j = [ 0.56934, -0.22911, 0.73042, 1.07319]
    c_j = [ 0.81061,  0.51059, 0.11899, 0.27195]
    m = -0.16398
    c =  0.63297

    # vertical K component
    k_V = k_compenet(freq, a_j, b_j, c_j, m, c)

    # a_H =========================================
    a_j = [-0.14318, 0.29591, 0.32177,-5.37610, 16.1721]
    b_j = [ 1.82442, 0.77564, 0.63773,-0.96230,-3.29980]
    c_j = [-0.55187, 0.19822, 0.13164, 1.47828, 3.43990]
    m =  0.67849
    c = -1.95537

    # horizontal A component
    a_H = a_component(freq, a_j, b_j, c_j, m, c)

    # a_V =========================================
    a_j = [-0.07771, 0.56727,-0.20238,-48.2991,  48.5833]
    b_j = [ 2.33840, 0.95545, 1.14520, 0.791669, 0.791459]
    c_j = [-0.76284, 0.54039, 0.26809, 0.116226, 0.116479]
    m = -0.053739
    c =  0.83433

    # vertical A component
    a_V = a_component(freq, a_j, b_j, c_j, m, c)


    # regression coefficients
    k = (k_H + k_V + (k_H - k_V) * (math.cos(math.radians(elev)) ** 2) * math.cos(math.radians(2 * tau))) / 2
    a = (k_H * a_H + k_V * a_V + (k_H * a_H - k_V * a_V) * (math.cos(math.radians(elev)) ** 2) * math.cos(math.radians(2 * tau))) / (2 * k)

    # specific attenuation, gamma_R (dB/km), is obtained from the rain rate, R (mm/h), using the power-law relationship
    gamma_R = k * (rainrate ** a)

    coefficents = [k, k_H, k_V, a, a_H, a_V]
    return gamma_R, coefficents 




# Helper funcs =====================================

def k_compenet(freq:float, a_j:list, b_j:list, c_j:list, m:float, c:float) -> float:
    '''
    Formula for K components with horizontal and vertical polarization

    Parameters:
        freq (GHz) : frequency
        a_j (list) : list of fitting coefficients
        b_j (list) : list of fitting coefficients
        c_j (list) : list of fitting coefficients
        m (float)  : fitting coefficient
        c (float)  : fitting coefficient

    Returns:
        k_component (float): k component term
    '''

    sum = 0
    for j in range(len(a_j)):
        term_j = a_j[j] * math.exp(-((math.log10(freq) - b_j[j])/ c_j[j])**2)
        sum += term_j

    k_compenet = 10 ** ( sum + m * math.log10(freq) + c) 

    return k_compenet


def a_component(freq:float, a_j:list, b_j:list, c_j:list, m:float, c:float) -> float:
    '''
    Formula for A components with horizontal and vertical polarization

    Parameters:
        freq (GHz) : frequency
        a_j (list) : list of fitting coefficients
        b_j (list) : list of fitting coefficients
        c_j (list) : list of fitting coefficients
        m (float)  : fitting coefficient
        c (float)  : fitting coefficient

    Returns:
        a_component (float): a component term
    '''
    sum = 0
    for j in range(len(a_j)):
        term_j = a_j[j] * math.exp(-((math.log10(freq) - b_j[j])/ c_j[j])**2)
        sum += term_j

    a_component = sum + m * math.log10(freq) + c  

    return a_component







def test():
    ## ========================================================
    #   test Cases are the examples at 
    #   https://www.mathworks.com/help/phased/ref/rainpl.html
    ## ========================================================

    # list of each test error precents
    error = []

    print ("\n specifc attenuation")

    gamma_r, coefficents = specific_attenuation(1,100,0,0)

    # gamma
    truth = 1.3671082691187344
    error.append((gamma_r - truth) * 100 / truth)
  

    # reference coeff from ITU-R 838-3
    # Frequency(GHz)    kH     aH     kV     aV
    # 1              2.59e-5 0.9691 3.08e-5 0.8592
    # 50              0.6600 0.8084 0.6472 0.7871
    # 60              0.8606 0.7656 0.8515 0.7486
    # 100             1.3671 0.6815 1.3680 0.6765
    # 1 000           1.3795 0.6396 1.3822 0.6365


    L_rain_light = rain_pl(10, 20, 1)
    truth = 0.9164266906624636
    error.append((L_rain_light - truth) * 100 / truth)

    L_rain_heavy = rain_pl(10, 20, 10)
    truth = 10.444287833375999
    error.append((L_rain_heavy - truth) * 100 / truth)


    # Frequency Sweep ====================

    L_rain = []
    freq_array = []
    range_km = 10
    rainrate = 20
    for freq in range(1,1001):
        L_rain.append(rain_pl(range_km,freq,rainrate))
        freq_array.append(freq)

    # Figure 1
    fig1, ax1 = plt.subplots()  # creates new figure like in matlab
    ax1.semilogx(freq_array, L_rain, color='green', linewidth=2)
    ax1.set_title(f"Rain Path Loss over {range_km} km as Frequency Sweep")
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Attenuation (dB)')
    ax1.grid(True)


    # Elevation Angle Sweep ===================

    L_rain = []
    elev = []
    range_km = 100
    freq_GHz = 100
    rainrate = 10
    for elevation in range(1,91):
        L_rain.append(rain_pl(range_km,freq_GHz,rainrate,elevation))
        elev.append(elevation)

    # Figure 2
    fig2, ax2 = plt.subplots() 
    ax2.plot(elev, L_rain, color='blue', linewidth=2)
    ax2.set_title(f"Rain Path Loss as Elevation Sweep for {range_km} km, {freq_GHz} GHz, {rainrate} mm/hr")
    ax2.set_xlabel('Elevation Angle (Degree)')
    ax2.set_ylabel('Attenuation (dB)')
    ax2.grid(True)


    # Tilt Angle (tau) Sweep ===================

    L_rain = []
    tau = []
    range_km = 100
    freq_GHz = 100
    rainrate = 10
    for tilt in range(-91,91):
        L_rain.append(rain_pl(range_km,freq_GHz,rainrate,0,tilt))
        tau.append(tilt)

    # Figure 3
    fig3, ax3 = plt.subplots() 
    ax3.plot(tau, L_rain, color='blue', linewidth=2)
    ax3.set_title(f"Rain Path Loss as Tilt Sweep for {range_km} km, {freq_GHz} GHz, {rainrate} mm/hr")
    ax3.set_xlabel('Tilt Angle (Degree)')
    ax3.set_ylabel('Attenuation (dB)')
    ax3.grid(True)


    tst_str = "Rainfall loss Test   : "

    # error loop
    max_error = max(error)
    tolerance = 1 # % 

    if (max_error == 0):
        tst_str += "Passed"
    elif(max_error < tolerance):
        tst_str += "Passed --within-tolerance"
    else:
        tst_str += f"Failed by {max_error}:.2f % "

    print(tst_str)

    return

if __name__ == "__main__":
    test()
    plt.show()