from Config import Config

class Node:
    '''
    Generic radio node class
    '''
    _total_nodes = 0

    def __init__(self, config:Config):
        '''
        Node Constructor
        
        Parameters:
            config (Config): radio parameter configuration
        '''
        self.__config   = config
        self.ID         = Node._total_nodes

        # Increment default node ID
        Node._total_nodes += 1

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, new_config):
        self.__config = new_config
