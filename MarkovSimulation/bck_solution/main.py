import logging
logging.getLogger().setLevel(logging.DEBUG)
import os
import pickle
import numpy as np

import pandas as pd

from modules.markow_chain import get_transistion_matrix, get_start_state_probabilities
import modules.simulation as simulation
import cv2
from modules.tiles_skeleton import SupermarketMap, MARKET, TILE_SIZE


dir_path = os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':

    mon_df=pd.read_csv(f"{dir_path}/data/monday.csv",sep=";")
    tue_df=pd.read_csv(f"{dir_path}/data/tuesday.csv",sep=";")
    wed_df=pd.read_csv(f"{dir_path}/data/wednesday.csv",sep=";")
    thu_df=pd.read_csv(f"{dir_path}/data/thursday.csv",sep=";")
    fri_df=pd.read_csv(f"{dir_path}/data/friday.csv",sep=";")
    day_dfs = [mon_df, tue_df, wed_df, thu_df, fri_df]

    transistion_matrix_path = f"{dir_path}/data/transistion_matrix"
    if(os.path.exists(transistion_matrix_path)):
        transistion_matrix = pickle.load(open(transistion_matrix_path, 'rb'))
    else :
        transistion_matrix = get_transistion_matrix(day_dfs)
        pickle.dump(transistion_matrix, open("transistion_matrix", "wb"))

    start_state_probabilities = get_start_state_probabilities(day_dfs)


    # visualization init
    tiles = cv2.imread(f"{dir_path}/modules/tiles.png")
    market = SupermarketMap(MARKET, tiles)
    background = np.zeros((500, 704, 3), np.uint8)
    frame = background.copy()
    avatars = []
    for i in range(1, 5):
        customer_icon_index = i%simulation.customer_icons_length
        y = simulation.customer_icons_pos[customer_icon_index][0] * TILE_SIZE
        x = simulation.customer_icons_pos[customer_icon_index][1] * TILE_SIZE
        tile = tiles[y:y+TILE_SIZE, x:x+TILE_SIZE]
        avatars.append(tile)

    # Add the customers
    init_tile_pos = simulation.entrance_pos
    starting_customers = [simulation.Customer.first(1, 'entrance', transistion_matrix, start_state_probabilities, market, avatars[0], init_tile_pos[0], init_tile_pos[1]), 
        simulation.Customer.first(2, 'entrance', transistion_matrix, start_state_probabilities, market, avatars[1], init_tile_pos[0], init_tile_pos[1]), 
        simulation.Customer.first(3, 'entrance', transistion_matrix, start_state_probabilities, market, avatars[2], init_tile_pos[0], init_tile_pos[1])]

    # Create a supermarket simulator from time 2022-03-03 07:00:00 to 2022-03-03 08:00:00
    supermarket = simulation.Supermarket(starting_customers, transistion_matrix,
                                        start_state_probabilities,
                                        pd.to_datetime('2022-03-03 07:00:00'),
                                        pd.to_datetime('2022-03-03 08:00:00'),3,frame,market, tiles)

    # Run the above simulator
    supermarket.simulate(f'{dir_path}/simulate.csv')

