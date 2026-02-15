import matplotlib.pyplot as plt
import numpy as np

def graph_total_pop(city):
    '''
    Test function to graph total population of a city over time.
    '''

    ypoints = np.array([week_data['city_data']['population'] for week_data in city.city_data.data])
    plt.plot(ypoints)
    plt.xlabel("Week")
    plt.ylabel("Population")
    plt.title(city.name)
    plt.show()
