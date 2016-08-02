import json
import pandas as pd
import multiprocessing
from functools import partial
import time
import csv
import numpy as np

tips = []
def load_categories():
    with open('../data/categories.txt') as f:
        json_str = f.read()
    return json.loads(unicode(json_str, "ISO-8859-1"))['response']

def get_categories(data):
    categories = {}
    cat_hierachy = {x['name']:x for x in data['categories']}
    for key, value in cat_hierachy.iteritems():
        categories[key] = value
    return categories

def get_sub_category_ids(category):
    ids = []
    for cat in category:
        ids.append(cat['id'])
    return ids

def load_tips_raw():
    global tips
    with open('../data/Tips/LA/LA-Tips.txt') as f:
        for line in f:
            tips.append(line.strip().split('\t'))

def load_users_tips():
    return pd.read_csv('../data/Tips/LA/LA-User-Tips.csv')


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


def load_tips_parallel(venues):
    pool = multiprocessing.Pool(4, initializer=load_tips_raw)  # for each core
    func = partial(load_tips, venues)
    num_range = xrange(1000)
    output = pool.map(func, num_range)
    # load_tips_raw()
    # output = load_tips_serial(venues, tips[:100])
    return output

def load_venues():
    venues = []
    with open('../data/Venues/LA/LA-Venues.txt') as f:
        for line in f:
            venues.append(line.strip().split('\t')[:14])
    df = pd.DataFrame(venues)
    cols = ['Venue_id', 'Venue_name', 'latitude', 'longitude', \
     'address', 'city', 'state', 'checkin_#', 'checked_user#', 'current_user#', 'todo#', \
     'category_#',  'category_id0', 'category_id1']
    df.columns = cols
    df['Venue_id'] = df['Venue_id'].apply(lambda x: str(x).strip('\"'))
    df['category_id1'] = df['category_id1'].apply(lambda x: str(x).strip('\"'))
    return df

def write_users_tips(user_tips, venues_df):
    with open('../data/Tips/LA/LA-User-Tips.csv', 'w+') as f:
         writer = csv.writer(f)
         writer.writerow(('User_ID', 'Venue_ID', 'Category_ID'))
         for tip in user_tips:
             for venue in tip[1]:
                 venue_id = venue.strip('\"')
                 writer.writerow((tip[0], venue_id, \
                  venues_df[venues_df['Venue_id'] == venue_id]['category_id1'].values[0]))

def build_usrlocation_matrix(user_tips, sub_categories):
    subset = user_tips[user_tips['Category_ID'].isin(sub_categories)]
    index = subset['User_ID'].unique()
    usrlocation_matrix = pd.DataFrame(index=index, columns=sub_categories)
    for i in index:
        for cat in sub_categories:
            usrlocation_matrix.ix[i][cat] = len((subset[subset['User_ID']==i])[subset['Category_ID']==cat].index)

    return usrlocation_matrix

def power_method(mat, start, maxit):
    """
    Does maxit iterations of the power method
    on the matrix mat starting at start.
    Returns an approximation of the largest
    eigenvector of the matrix mat.
    """
    result = start
    for i in xrange(maxit):
        result = np.dot(mat, result)
        result = result/np.linalg.norm(result)
    return result


if __name__=="__main__":
    data = load_categories()
    categories =  get_categories(data)
    sub_categories_shop = get_sub_category_ids(categories['Shop']['categories'])
    # sub_categories_shop = get_sub_category_ids(categories['Shop']['categories'])
    # sub_categories_shop = get_sub_category_ids(categories['Shop']['categories'])
    # sub_categories_shop = get_sub_category_ids(categories['Shop']['categories'])
    venues_df = load_venues()

    # start_time = time.time()
    # user_tips = load_tips_parallel(venues_df)
    # print time.time() - start_time
    # write_users_tips(user_tips, venues_df)

    user_tips = load_users_tips()
    usr_location_matrix = build_usrlocation_matrix(user_tips, sub_categories_shop)

    M = usr_location_matrix.as_matrix()
    user_hub__initial_score = usr_location_matrix.sum(axis=1).values
    user_hub_score = power_method(np.dot(M, M.T), user_hub__initial_score, 100)

    venue_auth_initial_score = usr_location_matrix.sum(axis=0).values
    venue_hub_score = power_method(np.dot(M.T, M), venue_auth_initial_score, 100)
