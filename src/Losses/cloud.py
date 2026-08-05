# Fog/Cloud attenuation model
#
# ONLY VALID for 1 - 200 GHz
#
# designed using
# ITU-R P.840-9 and MATLAB fogpl().m

import matplotlib.pyplot as plt



def cloud_pl(dist:float, freq:float, temp:float, density:float) -> float:
    '''
    Calculates path loss due to cloud / fog attenuation

    Parameters:
        dist      (km)    : path length
        freq      (GHz)   : path frequency
        Temp      (Kelvin): cloud tempature
        density   (g/m^3) : water vapor density in cloud

    Returns:
        total_attenation (dB): path loss
    '''
    
    #specific attenuation (dB/km)
    gamma = specific_attenuation(freq, temp, density)

    # total att. (dB)
    total_attenation = dist * gamma

    return total_attenation


def specific_attenuation(freq:float, temp:float, density:float) -> float:
    '''
    Calculates **specific** loss due to cloud / fog attenuation

    Parameters:
        freq      (GHz)   : path frequency
        Temp      (Kelvin): cloud tempature
        density   (g/m^3) : water vapor density in cloud

    Returns:
        specific_attenation (dB): specific cloud loss
    '''
    
    # elipsion constants
    e_0 = 77.66 + 103.3 * ((300 / temp) - 1)
    e_1 = 0.0671 * e_0
    e_2 = 3.52

    # Primary Relaxation freq
    f_p = 20.2 - 146 * ((300 / temp) - 1) + 316 * (((300 / temp) - 1) ** 2)
    # Secondary Relaxation freq
    f_s = 39.8 * f_p

    # dielectric permittivity of water - first order 
    term_1 = (e_0 - e_1) / (1 + (freq / f_p) ** 2)
    term_2 = (e_1 - e_2) / (1 + (freq / f_s) ** 2)
    elipsion_pri = term_1 + term_2 + e_2
    
    # dielectric permittivity of water - second order 
    term_1 = (freq * (e_0 - e_1)) / (f_p * (1 + (freq / f_p) ** 2)) 
    term_2 = (freq * (e_1 - e_2)) / (f_s * (1 + (freq / f_s) ** 2))
    elipsion_pri2 = term_1 + term_2

    # Nu equation
    nu = (2 + elipsion_pri) / elipsion_pri2

    # specific attenuation coefficient ((dB/km)/(g/m^3))
    K_l = (0.819 * freq) / (elipsion_pri2 * (1 + nu ** 2)) 

    # specific attenuation ((dB/km)/(g/m^3))
    gamma = K_l * density

    return gamma 






def test():
    ## ========================================================
    #   test Cases are the examples at 
    #   https://www.mathworks.com/help/phased/ref/fogpl.html
    ## ========================================================

    # Frequency Sweep ====================
    # attenuation in Cumulus Cloud
    # print("attenuation in Cumulus Cloud")
    dist    = 1     # (km)
    temp_C  = 20.0  # liquid temp (C)
    lwd     = 0.5   # liquid water densisty (g/m^3)
    temp    = temp_C + 273.15

    L = []
    x = []
    for freq in range(15,1001,5):
        L.append(cloud_pl(dist, freq, temp, lwd))
        x.append(freq)

    # Figure 1
    fig1, ax1 = plt.subplots()  # creates new figure like in matlab
    ax1.loglog(x, L, color='green', linewidth=2)
    ax1.set_title(f"Cumulus Cloud Path Loss (dB/km)")
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Attenuation (dB)')
    ax1.grid(True)
           
    print("Cloud/Fog loss Test  : Visually Confirm")

    return

if __name__ == "__main__":
    test()
    plt.show()