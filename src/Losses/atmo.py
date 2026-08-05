# Atmospheric Gas Attenuation Model
#
# ONLY VALID for 1 - 1,000 GHz and assumes no refraction (low alt)
#
# The maximum water vapor density of air at 30° C is approximately 30.0 g/m^3. The maximum water vapor density of air at 0°C is approximately 5.0 g/m^3
# Dry air pressure in Pa, specified as a positive real-valued scalar. One standard atmosphere at sea level is 101325 Pa
#
# designed using
# ITU-R P.676-13 and MATLAB gaspl().m

import matplotlib.pyplot as plt
import math
from Losses.freeSpace import fs_pl

def atmo_pl(dist:float, freq:float, Temp:float, Pressure:float, water_vapor_density:float) -> float:
    '''
    Calculates path loss due to atmospheric attenuation

    Parameters:
       dist      (km)    : path length
       freq      (GHz)   : path frequency
       Temp      (Kelvin): ambient tempature
       pressure  (Pa)    : atmospheric pressure
       water_vapor_density   (g/m^3) : water vapor density in air

    Returns:
       total_attenation (dB): path loss
    '''
    # converts to hPa
    P_tot = Pressure / 100

    # specific attenuation
    gamma = specific_attenuation(freq, Temp, P_tot, water_vapor_density)

    total_attenation = dist * gamma

    return total_attenation


def specific_attenuation(freq:float, Temp:float, P_tot:float, water_vapor_density:float) -> float:
    '''
    Calculates **specific** attenution of atmospheric path loss

    Parameters:
       freq      (GHz)   : path frequency
       Temp      (Kelvin): ambient tempature
       pressure  (Pa)    : atmospheric pressure
       water_vapor_density   (g/m^3) : water vapor density in air

    Returns:
       specific_attenation (dB): atmospheric specific loss
    '''

    # defined for convenience
    theta = 300 / Temp

    # wator vapor partial pressure (hPa)
    wet_P = (water_vapor_density * Temp) / 216.7

    # Dry air partial pressure (hPa)
    dry_P = P_tot - wet_P

    N_pri2_O = N_pri2_oxygen(freq, theta, dry_P, wet_P)

    # width parameter for Debye spectrum
    d = 5.6 * 1e-4 * P_tot * (theta ** 0.8)

    # dry continuum
    term_1 = (6.14 * 1e-5) / (d * (1 + (freq / d) ** 2))
    term_2 = (1.4 * 1e-12 * dry_P * (theta ** 1.5)) / (1 + 1.9 * 1e-5 * (freq ** 1.5))
    N_pri2_D = freq * dry_P * (theta ** 2) * (term_1 + term_2)

    # Adds pressure-induced nitrogen absorption 
    N_pri2_O += N_pri2_D


    N_pri2_W = N_pri2_water_vapor(freq, theta, dry_P, wet_P)

    # specific attenuation (dB/km) 
    # gamma = gamma_O + gamma_W
    gamma = 0.1820 * freq * (N_pri2_O + N_pri2_W) 

    return gamma


def N_pri2_oxygen(freq:float, theta:float, dry_P:float, wet_P:float) -> float:
    '''
    Helper func that returns N_pri2 for oxygen

    Parameters:
       freq (GHz): frequency
       theta (kelvin^-1): short hand for 300 / temp
       dry_P (hPa): dry atmo partial pressure
       wet_P (hPa): water vapor partial pressure

    Returns:
       N_pri2_oxygen (dB / (GHz * km)): TODO search ITU for return type and meaning
    '''
    f_0 = [50.47,50.99,51.50,52.02,52.54,53.07,53.60,54.13,54.67,55.22,
            55.78,55.78,56.36,56.97,57.61,58.32,58.45,59.16,59.59,60.31,
            60.43,61.15,61.80,62.41,62.49,63.00,63.57,64.13,64.68,65.22,
            65.76,66.30,66.84,67.37,67.90,68.43,68.96,118.75,368.50,
            424.76,487.25,715.39,773.84,834.15]
    
    a_1 = [0.98,2.53,6.19,14.32,31.24,64.29,124.60,227.30,389.70,627.10,
           945.30,945.30,1331.80,1746.60,2120.10,2363.70,1442.10,2379.90,
           2090.70,2103.40,2438.00,2479.50,2275.90,1915.40,1503.00,1490.20,
           1078.00,728.70,461.30,274.00,153.00,80.40,39.80,18.56,8.17,
           3.40,1.33,940.30,67.40,637.70,237.40,98.10,572.30,183.10]
    
    a_2 = [9.65,8.65,7.71,6.82,5.98,5.20,4.47,3.80,3.18,2.62,2.11,2.11,
           1.65,1.26,0.91,0.62,0.08,0.39,0.21,0.21,0.39,0.62,0.91,1.26,
           0.08,1.65,2.11,2.62,3.18,3.80,4.47,5.20,5.98,6.82,7.71,8.65,
           9.65,0.01,0.05,0.04,0.05,0.15,0.14,0.15]
    
    a_3 = [6.69,7.17,7.64,8.11,8.58,9.06,9.55,9.96,10.37,10.89,11.34,11.34,
           11.89,12.23,12.62,12.95,14.91,13.53,14.08,14.15,13.39,12.92,
           12.63,12.17,15.13,11.74,11.34,10.88,10.38,9.96,9.55,9.06,8.58,
           8.11,7.64,7.17,6.69,16.64,16.40,16.40,16.00,16.00,16.20,14.70]
    
    # a_4 is zero for all elements so contribnutes nothing to function thus excluded from memory

    a_5 = [2.57,2.25,1.95,1.67,1.39,1.35,2.23,3.17,3.56,2.56,-1.172,-1.172,
           -2.378,-3.545,-5.416,-1.932,6.77,-6.561,6.96,-6.395,6.34,1.01,
           5.01,3.03,-4.499,1.86,0.66,-3.036,-3.968,-3.528,-2.548,-1.660,
           -1.680,-1.956,-2.216, -2.492,-2.773 , -0.439 ,0.00,0.00,0.00,
           0.00,0.00,0.00]
    
    a_6 = [6.85,6.80,6.73,6.64,6.53,6.21,5.09,3.75,2.65,2.95,6.14,6.14,6.55,
           6.45,6.06,0.44,-1.273,2.31,-0.776,0.70,-2.825,-0.584,-6.619,-6.759,
           0.84,-6.675,-6.139,-2.895,-2.590,-3.680,-5.002,-6.091,-6.393,-6.475,
           -6.545, -6.6,-6.65,0.08,0.00,0.00,0.00,0.00,0.00,0.00]
    

    N_pri2_oxygen = 0
    for i in range(len(f_0)):
                   
       # atmospheric oxygen, each spectral line strength
       S_i_O = a_1[i] * (10 ** -7) * dry_P * (theta ** 3) * math.exp(a_2[i] * (1 - theta)) 

       # oxygen line frequency width
       deltaF = a_3[i] * (10 ** -4) * (dry_P * (theta ** 0.8) + 1.1 * wet_P * theta)

       # adjusted for Zeeman splitting
       deltaF = math.sqrt((deltaF ** 2) + 2.25 * 1e-6)

       # correction factor due to interference effects in Oxygen lines
       dirac = (a_5[i] + a_6[i] * theta) * 1e-4 * (wet_P + dry_P) * (theta ** 0.8)

       # Oxygen line shape factor
       term_1 = (deltaF - dirac * (f_0[i] - freq)) / ( ((f_0[i] - freq) **2) + (deltaF ** 2) )
       term_2 = (deltaF - dirac * (f_0[i] + freq)) / ( ((f_0[i] + freq) **2) + (deltaF ** 2) )  
       F_i_O = (freq / f_0[i]) * (term_1 + term_2)    

       N_pri2_oxygen += S_i_O * F_i_O

    return N_pri2_oxygen


def N_pri2_water_vapor(freq:float, theta:float, dry_P:float, wet_P:float) -> float:
    '''
    Helper func that returns N_pri2 for water vapor

    Parameters:
       freq (GHz): frequency
       theta (kelvin^-1): short hand for 300 / temp
       dry_P (hPa): dry atmo partial pressure
       wet_P (hPa): water vapor partial pressure

    Returns:
       N_pri2_water_vapor (dB / (GHz * km)): TODO search ITU for return type and meaning
    '''

    f_0 = [22.24,67.80,120.00,183.31,321.23,325.15,336.23,380.20,390.13,
           437.35,439.15,443.02,448.00,470.89,474.69,488.49,503.57,504.48,
           547.68,552.02,556.94,620.70,645.77,658.01,752.03,841.05,859.97,
           899.30,902.61,906.21,916.17,923.11,970.32,987.93,1780.00]
    
    b_1 = [0.11,0.00,0.00,2.27,0.05,1.51,0.00,11.67,0.00,0.06,0.91,0.19,
           10.41,0.33,1.26,0.25,0.04,0.01,0.98,0.18,497.00,5.02,0.01,0.27,
           243.40,0.01,0.13,0.05,0.04,0.18,8.40,0.01,9.01,134.60,17506.00]
    
    b_2 = [2.14,8.73,8.35,0.67,6.18,1.54,9.83,1.05,7.35,5.05,3.60,5.05,1.41,
           3.60,2.38,2.85,6.73,6.73,0.16,0.16,0.16,2.39,8.63,7.82,0.40,8.18,
           8.06,7.91,8.43,5.11,1.44,10.29,1.92,0.26,0.95]

    b_3 = [26.38,28.58,29.48,29.06,24.04,28.23,26.93,28.11,21.52,18.45,20.07,
           15.55,25.64,21.34,23.20,25.86,16.12,16.12,26.00,26.00,30.86,24.38,
           18.00,32.10,30.86,15.90,30.60,29.85,28.65,24.08,26.73,29.00,25.50,
           29.85,196.30]

    b_4 = [0.76,0.69,0.70,0.77,0.67,0.64,0.69,0.54,0.63,0.60,0.63,0.60,0.66,
           0.66,0.65,0.69,0.61,0.61,0.70,0.70,0.69,0.71,0.60,0.69,0.68,0.33,
           0.68,0.68,0.70,0.70,0.70,0.70,0.64,0.68,2.00]
    
    b_5 = [5.09,4.93,4.78,5.02,4.40,4.89,4.74,5.06,4.81,4.23,4.48,5.08,5.03,
           4.51,4.80,5.20,3.98,4.01,4.50,4.50,4.55,4.86,4.00,4.14,4.35,5.76,
           4.09,4.53,5.10,4.70,5.15,5.00,4.94,4.55,24.15]
    
    b_6 = [1.00,0.82,0.79,0.85,0.54,0.74,0.61,0.89,0.55,0.48,0.52,0.50,0.67,0.65,
           0.64,0.72,0.43,0.45,1.00,1.00,1.00,0.68,0.50,1.00,0.84,0.45,0.84,0.90,
           0.95,0.53,0.78,0.80,0.67,0.90,5.00]

    N_pri2_water_vapor = 0
    for i in range(len(f_0)):
            
       # atmospheric water vapor, each spectral line strength
       S_i_W = b_1[i] * (10 ** -1) * (theta ** 3.5) * math.exp(b_2[i] * (1 - theta)) * wet_P 

       # water vapor frequency line width
       deltaF = b_3[i] * 1e-4 * (dry_P * (theta ** b_4[i]) + b_5[i] * wet_P * (theta ** b_6[i]))

       # adjusted for Doppler broadening water vapor lines
       deltaF = 0.535 * deltaF + math.sqrt(0.217 * (deltaF ** 2) + (2.1326 * 1e-12 * (f_0[i] ** 2)) / theta )

       # water vapor line shape factor
       term_1 = (deltaF) / ( ((f_0[i] - freq) **2) + (deltaF ** 2) )
       term_2 = (deltaF) / ( ((f_0[i] + freq) **2) + (deltaF ** 2) )  
       F_i_W = (freq / f_0[i]) * (term_1 + term_2) 

       N_pri2_water_vapor += S_i_W * F_i_W


    return N_pri2_water_vapor




def test():
    ## ========================================================
    #   test Cases are the examples at 
    #   https://www.mathworks.com/help/phased/ref/gaspl.html
    ## ========================================================

    # atmospheric attenuation spectrum (dB/ km) =============== 
    #   with dry air comparison
    
    Temp_C          = 15        # C
    Pressure        = 101.3e3   # (Pa)
    vapor_density   = 7.5       # (g/m^3)

    Temp = Temp_C + 273.15

    L_dry = []
    L_wet = []
    x_GHz = []
    for freq in range(1,1000):
       L_dry.append(atmo_pl(1,freq,Temp,Pressure,0))
       L_wet.append(atmo_pl(1,freq,Temp,Pressure,vapor_density))
       x_GHz.append(freq)

    # Figure 1
    fig1, ax1 = plt.subplots()  # creates new figure like in matlab
    ax1.semilogy(x_GHz, L_wet, label='Standard', color='red', linewidth=2)
    ax1.semilogy(x_GHz, L_dry, label='Dry', color='blue', linewidth=2)
    ax1.set_title(f"Specific Atmospheric Attenuation : Humid and Dry")
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Specific Attenuation (dB/km)')
    ax1.legend()
    ax1.grid(True)



    # attenuation due to atmo and free space ====================
    # range sweep with L_fs and L_prop = L_fs + L_atmo

    # system parameters
    freq             = 10          # (GHz) : X-band radar
    Temp_C           = 20          # C
    Pressure         = 101.325e3   # (Pa)
    vapor_density    = 7.5         # (g/m^3)

    Temp = Temp_C + 273.15

    L_prop = []
    L_fs = []
    x_km = []
    for dist in range(1,101):
       free_space_loss = fs_pl(dist, freq)
       L_fs.append(free_space_loss)
       L_prop.append(atmo_pl(dist, freq, Temp, Pressure, vapor_density) + free_space_loss)
       x_km.append(dist)

    # Figure 2
    fig2, ax2 = plt.subplots()  
    ax2.semilogx(x_km, L_prop, label='Atmospheric + Free Space Loss', color='blue', linewidth=2)
    ax2.semilogx(x_km, L_fs, label='Free Space Loss', color='red', linewidth=2)
    ax2.set_title(f"Path Loss over {x_km[-1]} km")
    ax2.set_xlabel('Range (km)')
    ax2.set_ylabel('Loss (dB)')
    ax2.legend()
    ax2.grid(True)


    print("Atmospheric loss Test: Visually confirm")

    return

if __name__ == "__main__":
    test()
    plt.show()