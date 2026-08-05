class Config:
        '''
        radio parameter configuration
        '''

        def __init__(self):
            '''
            default config constructor
            '''

            self.L_rx   = 0     # reciver loss          (dB)
            self.L_tx   = 0     # transmitter loss      (dB)
            self.G_rx   = 0     # reciver gain          (dB)
            self.G_tx   = 0     # transmiter gain       (dB)
            self.P_tx   = 30    # transmit power        (dBm)
            self.noise  = -100  # reciver noise         (dBm)
            