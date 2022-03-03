from random import randint
import time

from pytest import Instance
from .markow_chain import add_missing_checkouts
from .tiles_skeleton import SupermarketMap, TILE_SIZE

import numpy as np
import pandas as pd
from sqlalchemy import false
class Customer :

    def __init__(self, id, state, transistion_matrix):
        self.state = state
        self.id = id
        self.transistion_matrix = transistion_matrix
        self.terrain = None
        self.avatar = None
        self.row = 0
        self.col = 0

    @classmethod
    def first(cls, id, state, transistion_matrix, terrain, avatar, row, col):

        instance = cls(id, state, transistion_matrix)
        instance.state = state
        instance.id = id
        instance.transistion_matrix = transistion_matrix
        instance.terrain = terrain
        instance.avatar = avatar
        instance.row = row
        instance.col = col
        return instance

    def next_state(self):
        if(self.is_active()):
            self.state = np.random.choice(self.transistion_matrix.columns, p = self.transistion_matrix.loc[self.state])
        return self.state

    def is_active(self):
        if(self.state == "checkout"):
            return False
        return True

    def __repr__(self):
        return f'<Customer {self.id} in {self.state}>'

    def draw(self, frame):
        if(self.terrain is not None and self.avatar is not None):
            y = self.row * TILE_SIZE
            x = self.col * TILE_SIZE
            frame[y:y + self.avatar.shape[0], x:x + self.avatar.shape[1]] = self.avatar
    
    def move(self, direction):
        new_row = self.row
        new_col = self.col

        if direction == 'up':
            new_row -= 1
        if direction == 'down':
            new_row += 1
        if direction == 'left':
            new_col -= 1
        if direction == 'right':
            new_col += 1

        if self.terrain.contents[new_row][new_col] == '.':
            self.col = new_col
            self.row = new_row

class Supermarket:
    """manages multiple Customer instances that are currently in the market.
    """

    def __init__(self, customers, transistion_matrix, first_state_probabilities, start_time, end_time):        
        # a list of Customer objects
        self.customers = customers
        self.transistion_matrix = transistion_matrix
        self.first_state_probabilities = first_state_probabilities
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time
        self.last_id = max([x.id for x in customers])

    def __repr__(self):
        return ''


    def print_customers(self):
        for customer in self.customers:
            print(f"{customer} at {self.current_time}")
        return None

    def next_minute(self):
        self.current_time += pd.Timedelta(1, 'm')
        for i, customer in enumerate(self.customers):
            self.customers[i].next_state()
    
    def add_new_customers(self):

        if(len(self.customers) < 10):
            n_new_customers = randint(5, 10)
            for i in range(n_new_customers):
                self.last_id += 1
                state = np.random.choice(self.first_state_probabilities.index, p = self.first_state_probabilities)
                self.customers.append(Customer(self.last_id, state, self.transistion_matrix))

    def remove_exitsting_customers(self):
        customer_ids = []
        self.customers = [x for x in self.customers if x.is_active()]
    
    def get_current_min_rows(self):
        states = []
        customer_nos = []
        timestamps = []
        for i, customer in enumerate(self.customers):
            states.append(self.customers[i].state)
            customer_nos.append(self.customers[i].id)
            timestamps.append(self.current_time)

        return pd.DataFrame({'timestamp':timestamps, 'customer_no':customer_nos, 'location':states})


    def simulate(self, csv_file = '', quick = False):
        df = pd.DataFrame(columns = ['timestamp', 'customer_no', 'location'])
        try:
            while(self.current_time != self.end_time):
                self.print_customers()
                df = pd.concat([df,self.get_current_min_rows()], ignore_index=True)
                self.remove_exitsting_customers()
                self.next_minute()
                self.add_new_customers()

                if(not quick):
                    time.sleep(1)
        except:
            if(csv_file != ''):
                df = add_missing_checkouts(df)
                df.to_csv(csv_file)

        
        if(csv_file != ''):
            df = add_missing_checkouts(df)
            df.to_csv(csv_file)
        







