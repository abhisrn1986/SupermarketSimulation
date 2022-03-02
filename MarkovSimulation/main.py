import logging
logging.getLogger().setLevel(logging.DEBUG)
import os
import pickle

import pandas as pd

from markow_chain import get_transistion_matrix

dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':


    transistion_matrix_path = f"{dir_path}/transistion_matrix"

    if(os.path.exists(transistion_matrix_path)):
        transistion_matrix = pickle.load(open(transistion_matrix_path, 'rb'))
    else :
        mon_df=pd.read_csv(f"{dir_path}/monday.csv",sep=";")
        tue_df=pd.read_csv(f"{dir_path}/tuesday.csv",sep=";")
        wed_df=pd.read_csv(f"{dir_path}/wednesday.csv",sep=";")
        thu_df=pd.read_csv(f"{dir_path}/thursday.csv",sep=";")
        fri_df=pd.read_csv(f"{dir_path}/friday.csv",sep=";")

        transistion_matrix = get_transistion_matrix([mon_df, tue_df, wed_df, thu_df, fri_df])

        pickle.dump(transistion_matrix, open("transistion_matrix", "wb"))

    print(transistion_matrix)

    






