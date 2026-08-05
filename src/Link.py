# Link Class used to describe the connection between two nodes

from Losses.rain        import rain_pl
from Losses.cloud       import cloud_pl
from Losses.atmo        import atmo_pl
from Losses.freeSpace   import fs_pl
from Losses.thermal     import thermal_noise_floor
from Environment        import Environment
from Node import Node

class Link:
    '''
    Used to describe the connection between two nodes with environmental conditions
    '''

    def __init__(self, N_tx:Node, N_rx:Node, environment:Environment):
        '''
        Link constructor

        Parameters:
            N_tx (Node): transmitting node
            N_rx (Node): receiving node
            environment (Environment): an configured Environment object
        '''
        self.N_tx           = N_tx
        self.N_rx           = N_rx
        self.env            = environment      # enviorment conditions
        self.distance       = 1     # km
        self.freq_GHz       = 1     # GHz
        self.elev_angle     = 0     # degrees
        self.polar_tilt     = 0     # degrees
        self.bandwidth      = 1 # MHz
        self.noise_floor    = thermal_noise_floor(self.bandwidth)

    
    def path_loss(self) -> float:
        '''
        Calculates total path loss with enviroment state logic
        
        Returns:
            Path Loss (dB): total path loss
        '''

        # extracted for shorter func calls
        env = self.env
        
        # free space loss is baseline loss
        L_fs = fs_pl(self.distance, self.freq_GHz)
        L_prop = L_fs

        # Atmo loss
        if env._is_atmo:
            # entire path is pressumed to be within atmosphere
            L_atmo = atmo_pl(self.distance, self.freq_GHz, env.temp, env.pressure_kPa * 1e3, env.water_vapor_density)
            L_prop += L_atmo

        # Cloud loss
        if env._is_cloudy:
            # Path covered by cloud
            cloud_path = env.cloud_path_per * self.distance
            L_cloud = cloud_pl(cloud_path, self.freq_GHz, env.cloud_temp, env.cloud_density)
            L_prop += L_cloud

        # Rain loss
        if env._is_raining:
            # Path covered by rain
            rain_path = env.rain_path_per * self.distance
            L_rain = rain_pl(rain_path, self.freq_GHz, env.rainrate, self.elev_angle, self.polar_tilt)
            L_prop += L_rain

        return L_prop


    def link_budget(self) -> float:
        '''
        Calculates link budget between transmitting and receiving nodes given the link conditions

        Returns:
            P_rx (dBm) : power received
        '''

        # Hardware system parameters        
        G_sys = self.N_tx.config.G_tx + self.N_rx.config.G_rx  # system gain   (dB)
        L_sys = self.N_tx.config.L_tx + self.N_rx.config.L_rx  # system loss   (dB)

        # calc propagation Losses
        L_prop = self.path_loss()

        Loss = L_prop + L_sys  # units : dB

        # System Gains
        Gain = G_sys

        # power recived at N_rx (dBm) 
        P_rx = self.N_tx.config.P_tx + Gain - Loss

        return P_rx  
    
    
    def link_SNR(self) -> float:
        '''
        Calculates the SNR assuming noise floor can be approximated as thermal noise
        
        Returns:
            snr (dB): signal to noise ratio in dB
        '''

        N_thermal = thermal_noise_floor(self.bandwidth * 1e6, self.env.temp)

        # assuming thermal noise is dominate noise
        self.noise_floor = N_thermal

        P_rx = self.link_budget()

        snr = P_rx - self.noise_floor

        return snr