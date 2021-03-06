import logging
import time
import traceback
from random import randint, choice
from matplotlib.pyplot import grid

import numpy as np
import pandas as pd
from pytest import Instance
from sqlalchemy import false
import cv2

from .markow_chain import add_missing_checkouts
from .tiles_skeleton import TILE_SIZE, SupermarketMap, MARKET
from .a_star import find_path

customer_icons_pos = [[4,1],[4,15],[5,15],[6,15],[7,15],[8,15],[11,15],[7,0]]
customer_icons_length = len(customer_icons_pos)
entrance_pos = [10,4]
checkout_pos = [10,14]
section_to_position = {'fruit': [1,5], 'spices': [3,10], 'dairy': [6,14], 'drinks':[8,18], 'checkout' : checkout_pos , 'entrance': entrance_pos}

def get_random_position(section):

    if(section == 'fruit') :
        return [randint(1,6), choice([3,6])]
    if(section == 'spices') :
        return [randint(1,6), choice([7,10])]
    if(section == 'dairy') :
        return [randint(1,6), choice([11,14])]
    if(section == 'drinks') :
        return [randint(1,6), choice([15,18])]
    if(section == 'entrance'):
        return entrance_pos
    if(section == 'checkout'):
        return checkout_pos
    

def get_grid(grid_string):
    row_strings = grid_string.split('\n')

    n_rows = len(row_strings)
    n_cols = len(row_strings[0])
    grid = np.ones((n_rows, n_cols), dtype=int)
    
    for row, s in enumerate(row_strings):
        for col, c in enumerate(s):
            if(c == '.'):
                grid[row,col] = 0
    return grid
    
def get_path(grid, start, end):
    possible_moves = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    return find_path(grid, start, end, possible_moves)

class Customer :

    def __init__(self, id, state, transistion_matrix, start_probabilities):
        self.state = state
        self.id = id
        self.transistion_matrix = transistion_matrix
        self.terrain = None
        self.avatar = None
        self.row = entrance_pos[0]
        self.col = entrance_pos[1]
        self.path = np.array([])
        self.grid = None
        self.start_probabilities = start_probabilities


    @classmethod
    def first(cls, id, state, transistion_matrix, start_probabilities, terrain, avatar, row, col):
        instance = cls(id, state, transistion_matrix, start_probabilities)
        instance.state = state
        instance.id = id
        instance.transistion_matrix = transistion_matrix
        instance.terrain = terrain
        instance.avatar = avatar
        instance.row = row
        instance.col = col
        instance.path = np.array([])
        instance.grid = get_grid(terrain.layout)
        instance.start_probabilities = start_probabilities
        return instance

    def next_state(self):
        if(self.is_active()):
            self.prev_state = self.state
            if(self.state == 'entrance') :
                self.state = np.random.choice(self.start_probabilities.index, p = self.start_probabilities)
            else:
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

    def next_node(self) :
        if(np.size(self.path) != 0 and np.size(self.path[1:]) != 0):
            self.row = self.path[1][0]
            self.col = self.path[1][1]
            self.path = self.path[1:]
        
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

    def __init__(self, customers, transistion_matrix, first_state_probabilities, start_time, end_time,
                max_customers_no, frame = None, terrain = None, tiles = None):        
        # a list of Customer objects
        self.customers = customers
        self.transistion_matrix = transistion_matrix
        self.first_state_probabilities = first_state_probabilities
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time
        self.last_id = max([x.id for x in customers])
        self.frame = frame
        self.terrain = terrain
        self.tiles = tiles
        self.max_customers_no = max_customers_no

    def __repr__(self):
        return ''

    def print_customers(self):
        for customer in self.customers:
            print(f"{customer} at {self.current_time}")
    
    def draw_customers(self):
        for customer in self.customers:
            customer.draw(self.frame)
            customer.next_node()

    def next_minute(self):
        self.current_time += pd.Timedelta(1, 'm')
        for i, customer in enumerate(self.customers):
            self.customers[i].next_state()

    
    def add_new_customers(self):

        n_customers = len(self.customers)
        if(n_customers < self.max_customers_no):
            n_new_customers = self.max_customers_no - n_customers
            for i in range(n_new_customers):
                self.last_id += 1
                state = "entrance"
                if(self.frame is None):
                    self.customers.append(Customer(self.last_id, state, self.transistion_matrix, self.first_state_probabilities))
                else:
                    customer_icon_index = self.last_id%customer_icons_length
                    y = customer_icons_pos[customer_icon_index][0] * TILE_SIZE
                    x = customer_icons_pos[customer_icon_index][1] * TILE_SIZE
                    self.customers.append(Customer.first(self.last_id, state, self.transistion_matrix, self.first_state_probabilities, 
                    self.terrain, self.tiles[y:y+TILE_SIZE, x:x+TILE_SIZE], entrance_pos[0],entrance_pos[1]))
                    self.customers[-1].draw(self.frame)

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
    
    def all_customers_reached_target(self):
        for i, customer in enumerate(self.customers):
            node = customer.path[-1] 
            if(node[0] != customer.row or node[1] != customer.col):
                return False
        
        return True
            
    def calculate_paths(self):
        for i_customer, customer in enumerate(self.customers):
            # end_pos = tuple(section_to_position[customer.state])
            end_pos = tuple(get_random_position(customer.state))
            start_pos = (customer.row, customer.col)
            self.customers[i_customer].path = np.array(get_path(self.grid, start_pos, end_pos))
            

    def simulate(self, csv_file = '', quick = False):
        df = pd.DataFrame(columns = ['timestamp', 'customer_no', 'location'])
        background = np.zeros((500, 704, 3), np.uint8)

        self.grid = get_grid(MARKET)
        
        # number of seconds timestep
        self.next_minute()
        self.calculate_paths()

        try:
            while(self.current_time != self.end_time):
                self.frame = background.copy()
                self.terrain.draw(self.frame)
                key = cv2.waitKey(10)
                df = pd.concat([df,self.get_current_min_rows()], ignore_index=True)
                self.draw_customers()
                cv2.imshow("frame", self.frame)

                if(self.all_customers_reached_target()):
                    self.add_new_customers()
                    self.print_customers()
                    self.remove_exitsting_customers()
                    self.next_minute()
                    self.calculate_paths()

                if key == 113: # 'q' key
                    break

                if(not quick):
                    time.sleep(1) 
        except Exception as e:
            cv2.destroyAllWindows()
            if(csv_file != ''):
                df = add_missing_checkouts(df)
                df.to_csv(csv_file)
            logging.error(traceback.format_exc())

        cv2.destroyAllWindows()

        if(csv_file != ''):
            df = add_missing_checkouts(df)
            df.to_csv(csv_file)
