import logging
logging.getLogger().setLevel(logging.DEBUG)
import os
import pickle

import pandas as pd

from markow_chain import get_transistion_matrix, get_start_state_probabilities
from simulation import Customer, Supermarket

dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':

    transistion_matrix_path = f"{dir_path}/transistion_matrix"
    mon_df=pd.read_csv(f"{dir_path}/monday.csv",sep=";")
    tue_df=pd.read_csv(f"{dir_path}/tuesday.csv",sep=";")
    wed_df=pd.read_csv(f"{dir_path}/wednesday.csv",sep=";")
    thu_df=pd.read_csv(f"{dir_path}/thursday.csv",sep=";")
    fri_df=pd.read_csv(f"{dir_path}/friday.csv",sep=";")
    day_dfs = [mon_df, tue_df, wed_df, thu_df, fri_df]

    if(os.path.exists(transistion_matrix_path)):
        transistion_matrix = pickle.load(open(transistion_matrix_path, 'rb'))
    else :
        transistion_matrix = get_transistion_matrix(day_dfs)
        pickle.dump(transistion_matrix, open("transistion_matrix", "wb"))

    start_state_probabilities = get_start_state_probabilities(day_dfs)

    starting_customers = [Customer(1, 'fruit', transistion_matrix), 
        Customer(2, 'dairy', transistion_matrix), 
        Customer(3, 'spices', transistion_matrix)]

    supermarket = Supermarket(starting_customers, transistion_matrix,
        start_state_probabilities,
        pd.to_datetime('2022-03-03 07:00:00'),
        pd.to_datetime('2022-03-03 08:00:00'))

    supermarket.simulate()

        
    






