class Environment:
    '''
    Enviorment class that is used to describe enviromental conditions such as rain or atmosphere
    '''
    def __init__(self):

        # env logic
        self._is_raining            = False
        self._is_cloudy             = False
        self._is_atmo               = False 

        # Atmospheric 
        self.temp_C                 = 20
        self.pressure_kPa           = 101.3
        self.humidity               = 0.5
        
        # Cloud 
        self.cloud_temp_C           = 20    # Celcius
        self.cloud_density          = 7.5   # g/m^3 
        self.water_vapor_density    = self.rel_hum_2_WV_density(self.humidity, self.Celcius_to_Kelvin(self.temp_C)) # g/m^3
        self.cloud_path_per         = 1     # cloud path distance

        
        # Rain 
        self.rainrate       = 0     # mm/hr
        self.rain_path_per  = 0     # rain path distance

        
    def update(self):
        '''
        Updates object tempatures units, water vapor density 
        '''
        # converts temp units
        self.cloud_temp = self.Celcius_to_Kelvin(self.cloud_temp_C) 
        self.temp       = self.Celcius_to_Kelvin(self.temp_C)

        # Update water vapor density
        self.water_vapor_density = self.rel_hum_2_WV_density(self.humidity,self.temp)

    
        

    @staticmethod
    def Celcius_to_Kelvin(celcius):
        '''
        converts from celcius to kelvin
        '''
        kelvin = celcius + 273.15
        return kelvin

    @staticmethod
    def rel_hum_2_WV_density(Relative_Humidity:float, Temp_K:float) -> float:
        '''
        Converts from Relative humidity to water vapor density

        Parameters:
            Relative_Humidity (float): unity float of humidity precentage
            temp_k (float) : tempature (kelvin) of atmosphere

        Returns:
           Vapor_density (float): water vapor density (g/m^3) 
        '''

        # relative humidity % = (vapor density / saturation vapor density) * 100% 
        # saturation vapor density (SVD) is apporx 4.85 g/m^3 @ 273 K = 0 Celsius
        P_SVD_0 = 4.85  # (g/m^3)

        # pressure of Saturation Vapor Density at ambient temp
        P_SVD   = (P_SVD_0 * Temp_K) / 273

        Vapor_density = Relative_Humidity * P_SVD

        return Vapor_density