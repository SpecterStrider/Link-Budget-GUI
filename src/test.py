# runs test cases for all files in link budget
import Losses.rain      as rain
import Losses.cloud     as cloud
import Losses.atmo      as atmo
import Losses.freeSpace as freeSpace  
import Losses.thermal   as thermal  

from Node import * 
from Plot import Plot
from Link import Link
from Environment import Environment

import matplotlib.pyplot as plt


# # Final plot ================================

if __name__ == "__main__":

    print("\n Loss test: ")

    rain.test()
    cloud.test()
    atmo.test()
    freeSpace.test()
    thermal.test()

    print("\n Object test: ")


    default_config      = Config()
    default_link_env    = Environment()
    default_node        = Node(default_config)
    default_link        = Link(default_node, default_node, default_link_env)
    plot                = Plot()

    default_link.bandwidth = 500

    default_link.env.update()

    print(default_link.link_budget())
    print(default_link.noise_floor)
    print(default_link.link_SNR())

    plt.show()
