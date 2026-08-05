# Thermal Noise
#
# # designed using
# Johnson–Nyquist thermal noise floor

import math

def thermal_noise_floor(bandwidth:float, temp_k:float=290):
    '''
    calculates thermal noise floor \n
    N = kBT
    
    Parameters:
        bandwidth (hertz)   : signal bandwidth
        temp_k (kelvin)     : environment tempature

    Returns:
        N_dBm (dBm) : thermal noise 
    '''
    # Boltzman constant (Joules / (Hz * Kelvin))
    k = 1.380649 * (10 ** -23)

    # linear
    N = k * bandwidth * temp_k

    # dB land
    N_dBm = 10 * math.log10(N)

    return N_dBm


def test():
    ## ========================================================
    #   test cases 
    ## ========================================================

    N_therm = thermal_noise_floor(1e6, 290)
    truth   = 20
    error_precent = (N_therm - truth) * 100 / truth
    tolerance = 1 # 1%

    tst_str = "Thermal Noise Test   : "
    if (error_precent == 0):
        tst_str += "Passed"
    elif(error_precent < tolerance):
        tst_str += "Passed --within-tolerance"
    else:
        tst_str += f"Failed by {error_precent}:.2f % "
    
    print(tst_str)

    return

