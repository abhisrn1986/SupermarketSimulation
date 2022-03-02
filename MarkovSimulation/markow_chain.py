import logging
import pandas as pd
import numpy as np
logging.getLogger().setLevel(logging.DEBUG)


# add the checkout rows for customers who dont have a checkout timestamp
def add_missing_checkouts(df, checkout_label = 'checkout') :
    add_rows = df.groupby('customer_no').filter(lambda x : all(x['location'] != 'checkout')).groupby('customer_no').agg({'timestamp':max})
    add_rows['location'] = checkout_label
    add_rows['timestamp'] = pd.to_datetime(add_rows['timestamp']) + pd.Timedelta(1, 'm') 

    # we need to have an index here to properly concatenate the rows
    # to the initial supermarket dataframes
    add_rows.reset_index(inplace=True)

    return pd.concat([df, add_rows], ignore_index=True)

def get_timespent_location(x, df):
    if x['location'] == "checkout":
        return 0
    else:
        return (df.iloc[x.name + 1]['timestamp'] - x['timestamp']).seconds/60

def customer_total_revenue(df, customer_id, revenue_per_minute) :
    try: 
        customer_df = df.loc[customer_id == df['customer_no']].sort_values(by=['timestamp'])
        customer_df.reset_index(inplace=True)
        customer_df["location_time_spent"] = customer_df.apply(get_timespent_location, args=(customer_df,), axis=1)
        print(customer_df[['location', 'location_time_spent']][:-1].groupby("location").sum())

    except KeyError:
        print(f"Check the customer id {customer_id}")
    
    # return customer_df
    return customer_df[['location', 'location_time_spent']][:-1].groupby("location").sum().apply(lambda x : revenue_per_minute.loc[x.name]['revenue_per_min'] * x, axis=1)


import logging

logging.getLogger().setLevel(logging.INFO)


def get_customer_transitions(df, customer_id):
    customer_transitions = df.loc[customer_id == df['customer_no']].sort_values(by=['timestamp'])

    logging.debug(customer_transitions)
    minutes = int((customer_transitions["timestamp"].max() - customer_transitions["timestamp"].min()).seconds/60)
    current_state = customer_transitions.iloc[0]["location"]
    minute_transistions = [current_state]

    minute_delta = pd.Timedelta(1, 'm')
    timestamp = customer_transitions.iloc[0]["timestamp"] + minute_delta
    row_index = 1
    last_index = customer_transitions.shape[0]

    next_timestamp = customer_transitions.iloc[row_index]["timestamp"]

    for minute in range(minutes) :
        logging.debug(f"current time {timestamp}" )
        logging.debug(f"next time {next_timestamp}")

        # Other way to do this however below method is more efficient
        # if (customer_transitions["timestamp"] == timestamp).any():
        #     current_state = customer_transitions.loc[customer_transitions["timestamp"] == timestamp]['location'].iloc[0]

        if timestamp == next_timestamp:
            current_state = customer_transitions.iloc[row_index]["location"]
            row_index += 1
            if(row_index < last_index):
                next_timestamp = customer_transitions.iloc[row_index]["timestamp"]
            logging.debug(f"changed to {current_state}")
        
        minute_transistions.append(current_state)
        timestamp += minute_delta

    return minute_transistions


def get_transistion_matrix(day_dfs):

    n_customers = 0
    for df in day_dfs:
        n_customers += len(df['customer_no'].unique())
    n_customers

    all_days_df = pd.DataFrame()

    for df in day_dfs:
        all_days_df = all_days_df.append(add_missing_checkouts(df), ignore_index=True)

    all_days_df["timestamp"] = pd.to_datetime(all_days_df["timestamp"])
    all_days_df['weekday'] = all_days_df['timestamp'].dt.weekday


    # add ids of the customers
    max_customer_numbers = all_days_df.groupby(['weekday'])['customer_no'].max()
    max_customer_numbers = max_customer_numbers.shift(1)
    max_customer_numbers[0] = 0
    max_customer_numbers = max_customer_numbers.astype(int).cumsum()
    customers_column = all_days_df.apply(lambda x : x['customer_no'] + max_customer_numbers[x['weekday']], axis=1)
    customers_column.name = "customer_no"
    all_days_df.update(customers_column)

    logging.info(all_days_df)

    overall_transistions = pd.DataFrame()

    for i in range(1, n_customers + 1):
        try:
            customer_transitions = get_customer_transitions(all_days_df, i)
            states = pd.DataFrame(customer_transitions)
            states.rename({0:"section"}, inplace=True, axis=1)
            states['section_next_minute'] = states['section'].shift(-1)
        except:
            print("Error at ", i)

        # states.dropna(inplace=True)
        overall_transistions = pd.concat([overall_transistions, states], ignore_index=True)

    overall_transistions.dropna(inplace=True)

    return pd.crosstab(overall_transistions['section'], overall_transistions['section_next_minute'], normalize=0)
    