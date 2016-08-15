import pandas as pd
import numpy as np
import venues
import multiprocessing
from functools import partial
import csv
import time
import categories as cat
import users

tips = []
def load_tips_raw():
    global tips
    with open('../data/Tips/NYC/NYC-Tips.txt') as f:
        for line in f:
            tips.append(line.strip().split('\t'))

def load_tips(venues_df, index):
    venue_list = [v.strip('\"') \
      for v in tips[index][1:] if v.strip('\"') in venues_df['Venue_id'].values]
    return (tips[index][0], venue_list)

def load_tips_serial(venues_df, tips):
    user_tips = {}
    for tip in tips:
        venue_list = [v for v in tip[1:] if v in venues_df['Venue_id'].values]
        user_tips[tip[0]] = venue_list
    return user_tips

def load_tips_parallel(venues_df):
    pool = multiprocessing.Pool(4, initializer=load_tips_raw)
    func = partial(load_tips, venues_df)
    num_range = xrange(500)
    output = pool.map(func, num_range)
    # load_tips_raw()
    # output = load_tips_serial(venues, tips[:100])
    return output

def write_users_tips(user_tips, venues_df):
    with open('../pre_500/Tips/NYC/NYC-User-Tips-500.csv', 'w+') as f:
         writer = csv.writer(f)
         writer.writerow(('User_ID', 'Venue_ID', 'Category_ID'))
         for tip in user_tips:
             for venue in tip[1]:
                 venue_id = venue.strip('\"')
                 writer.writerow((tip[0], venue_id, \
                  venues_df[venues_df['Venue_id'] == venue_id]['category_id1'].values[0]))

def load_raw_data():
    venues.load_venues()
    cat.load_categories()
    users.load_users_tips_500()
    #users.load_users_tips()

def preprocess_usr_tips():
    start_time = time.time()
    venues_df = venues.getVenues()
    user_tips = load_tips_parallel(venues_df)
    print time.time() - start_time
    write_users_tips(user_tips, venues_df)

def preprocess_social_learning_highlevel_cat_scores():
    high_level = cat.get_categories()
    for key in high_level.keys():
        sub_categories_ids = \
            cat.get_sub_category_ids(high_level[key]['categories'])
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                     users.user_venue_scores_by_category_precompute(sub_categories_ids)
        np.save('../pre_500/scores/'+ key+"_nyc_user_hub_score", user_hub_score)
        np.save('../pre_500/scores/'+ key+"_nyc_venue_hub_score", venue_hub_score)
        np.save('../pre_500/scores/'+ key+"_nyc_users_index", users_index)
        np.save('../pre_500/scores/'+ key+"_nyc_users_location_matrix", usr_location_matrix)

def preprocess_social_learning_venue_scores():
    high_level = cat.get_categories()
    sub_dict = cat.get_sub_categories_id_dict(high_level)
    for key in sub_dict.keys():
        cat_id = sub_dict[key]
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                users.user_venue_scores_by_venue_precompute(cat_id)
        np.save('../pre_500/scores/'+ key +"_nyc_user_hub_score", user_hub_score)
        np.save('../pre_500/scores/'+ key +"_nyc_venue_hub_score", venue_hub_score)
        np.save('../pre_500/scores/'+ key +"_nyc_users_index", users_index)
        np.save('../pre_500/scores/'+ key+"_nyc_users_location_matrix", usr_location_matrix)




if __name__ == "__main__":
    load_raw_data()
    # preprocess_usr_tips()
    # preprocess_social_learning_highlevel_cat_scores()
    preprocess_social_learning_venue_scores()
