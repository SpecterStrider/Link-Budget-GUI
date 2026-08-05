# free space loss
# see friis transmission equation
# assumes distance is much greater than wavelength
# i.e. both anntenas are in the far field region

import math

def fs_pl(dist_km, freq_GHz):
    '''
    Calculates path free space loss 

    Parameters:
        dist (km) : path distance
        freq (GHz): path frequency

    Returns:
        L_fs (dB) : path free space loss
    '''

    c                = 2.99792458e8 # (m/s)
    wavelength       = c / (freq_GHz * 1e9)

    # free space path loss (dB)
    L_fs = 20 * math.log10(4*math.pi* (dist_km*1e3) /  wavelength)     

    if ((dist_km*1e3) <= (wavelength  / 4 * math.pi)):
        L_fs = 0

    return L_fs


def test():

    range = 10    # km
    freq  = 10    # GHz
    L = fs_pl(range,freq)
    status = "Failed"
    truth = 132.4478
    tolerance = 1 # % tolerance
    error_precent = ( L - truth) * 100 / truth
    if ( error_precent < tolerance): 
        status = "Passed"
    else:
        status = f"Failed by {error_precent} %"

    print(f"Free space loss Test : {status}")
    
    return

if __name__ == "__main__":
    test()