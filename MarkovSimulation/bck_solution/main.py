import logging
logging.getLogger().setLevel(logging.DEBUG)
import os
import pickle
import numpy as np

import pandas as pd

from modules.markow_chain import get_transistion_matrix, get_start_state_probabilities
from modules.simulation import Customer, Supermarket
import cv2
from modules.tiles_skeleton import SupermarketMap, MARKET, TILE_SIZE


dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':

    # visualization init
    tiles = cv2.imread(f"{dir_path}/modules/tiles.png")
    y = 7*TILE_SIZE
    x = 0*TILE_SIZE
    tile = tiles[y:y+TILE_SIZE, x:x+TILE_SIZE]
    init_tile_pos = [0,7]
    market = SupermarketMap(MARKET, tiles)

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

    # starting_customers = [Customer(1, 'fruit', transistion_matrix, market, tile, init_tile_pos[0], init_tile_pos[1]), 
    #     Customer(2, 'dairy', transistion_matrix, market, tile, init_tile_pos[0], init_tile_pos[1]), 
    #     Customer(3, 'spices', transistion_matrix, market, tile, init_tile_pos[0], init_tile_pos[1])]
    starting_customers = [Customer(1, 'fruit', transistion_matrix), 
        Customer(2, 'dairy', transistion_matrix), 
        Customer(3, 'spices', transistion_matrix)]

    supermarket = Supermarket(starting_customers, transistion_matrix,
        start_state_probabilities,
        pd.to_datetime('2022-03-03 07:00:00'),
        pd.to_datetime('2022-03-03 08:00:00'))

    supermarket.simulate(f'{dir_path}/simulate.csv')


    # code for visualization

    # customer = Customer.first(1, 'fruit', transistion_matrix, market, tiles[y:y+TILE_SIZE, x:x+TILE_SIZE], 0,7)

    # background = np.zeros((500, 704, 3), np.uint8)

    # while True:
    #     frame = background.copy()
    #     market.draw(frame)
    #     customer.draw(frame)

    #     # https://www.ascii-code.com/
    #     key = cv2.waitKey(1)
       
    #     if key == 113: # 'q' key
    #         break
    #     # 119 is the 'w' key
    #     if key == 119:
    #         customer.move('up')
    #     if key == 115:
    #         customer.move('down')
    #     if key == 97:
    #         customer.move('left')
    #     if key == 100:
    #         customer.move('right')
    
    #     cv2.imshow("frame", frame)


    # cv2.destroyAllWindows()

    # market.write_image("supermarket.png")

