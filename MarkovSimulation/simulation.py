import numpy as np
import pandas as pd
from sqlalchemy import false

from random import randint
import time


class Customer :
    def __init__(self, id, state, transistion_matrix):

        self.state = state
        self.id = id
        self.transistion_matrix = transistion_matrix


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
            n_new_customers = randint(0, 10)
            for i in range(n_new_customers):
                self.last_id += 1
                state = np.random.choice(self.first_state_probabilities.index, p = self.first_state_probabilities)
                self.customers.append(Customer(self.last_id, state, self.transistion_matrix))

        
        return None

    def remove_exitsting_customers(self):
        customer_ids = []
        self.customers = [x for x in self.customers if x.is_active()]
        return None

    def simulate(self):
        while(self.current_time != self.end_time):
            self.print_customers()
            self.remove_exitsting_customers()
            self.next_minute()
            self.add_new_customers()
            time.sleep(1)






