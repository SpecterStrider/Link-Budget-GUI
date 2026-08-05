class Plot:
    '''Holds plot state and parmeters'''
    def __init__(self):
        #plot settings
        self.plot_noise_floor        = False

        # plot parameters
        self.plot_type               = "Link Budget" # "SNR"
        self.sweep_type              = "distance"    # "frequency"

        # frequency sweep parameters
        self._is_freq_sweep          = False
        self.freq_sweep_distance     = 1     # km
        self.start_freq              = 1
        self.stop_freq               = 1000

        # distance sweep parameters
        self._is_dist_sweep          = True
        self.dist_sweep_frequency    = 1    # GHz
        self.stop_distance           = 100  # km 
    