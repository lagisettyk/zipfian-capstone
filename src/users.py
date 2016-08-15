import pandas as pd
import numpy as np
import power_method
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import OrderedDict
import categories as cat

users_df = None
#user_pref_level2 = {}
#user_pref_level1 = {}
users_NJ = None
city = None

def load_users():
    global users_NJ
    usrs = []
    with open('../data/Users/LA/LA-Users.txt') as f:
        for line in f:
            row = line.strip().split('\t')
            city = row[-1].split(',')
            if len(city) == 2:
                usrs.append([row[0], city[0].strip('"'), city[1].strip('"').strip()])

    with open('../data/Users/NYC/NYC-Users.txt') as f:
        for line in f:
            row = line.strip().split('\t')
            city = row[-1].split(',')
            if len(city) == 2:
                usrs.append([row[0], city[0].strip('"'), city[1].strip('"').strip()])

    df = pd.DataFrame(usrs)
    cols = ['User id', 'city', 'state']
    df.columns = cols
    users_NJ = df[df['state']=='NJ']


def load_users_tips_500():
    global users_df, city
    users_df = pd.read_csv('../pre_500/Tips/NYC/NYC-User-Tips-500.csv')

def load_users_tips():
    global users_df, city
    print "+++++++++++==========: ", city
    if city != 'LA':
        users_df = pd.read_csv('../pre_500/Tips/NYC/NYC-User-Tips-500.csv')
    else:
        users_df = pd.read_csv('../pre_500/Tips/LA/LA-User-Tips-500.csv')

def get_visited_users(venue_list):
    return users_df[users_df['Venue_ID'].isin(venue_list)]['User_ID'].values

def get_venues_filered_by_users(usr_list):
    return users_df[users_df['User_ID'].isin(usr_list)]['Venue_ID'].values

def build_usrlocation_matrix(sub_categories):
    subset = users_df[users_df['Category_ID'].isin(sub_categories)]
    index = subset['User_ID'].unique()
    usrlocation_matrix = pd.DataFrame(index=index, columns=sub_categories)
    for i in index:
        for cat in sub_categories:
            usrlocation_matrix.ix[i][cat] = len((subset[subset['User_ID']==i])[subset['Category_ID']==cat].index)
    return usrlocation_matrix, index

def build_usrlocation_matrix_by_venues(cat_id):
    subset = users_df[users_df['Category_ID']==cat_id]
    index = subset['User_ID'].unique()
    cols = subset['Venue_ID'].unique()
    usrlocation_matrix = pd.DataFrame(index=index, columns=cols)
    for i in index:
        for col in cols:
            usrlocation_matrix.ix[i][col] = len((subset[subset['User_ID']==i])[subset['Venue_ID']==col].index)
    return usrlocation_matrix, index

def categoryid_to_doc(catids, categories, level=2):
    usr_category_doc = ''
    for key in categories.keys():
        for cat in categories[key]['categories']:
            if cat['id'] in catids:
                if level == 2:
                    # usr_category_doc += cat['name'].replace (" ", "_") + ' '
                    usr_category_doc += cat['name'] + '||'
                else:
                    #  usr_category_doc += str(hash(key)) + ' '
                    #usr_category_doc += key + ' '
                    usr_category_doc += key + '||'
    return usr_category_doc

def tokenize(doc):
    return [word for word in doc.rstrip('||').split('||')]

def get_peronalpreference_vectors(vocab, user_pref_values):
    tokens = tokenize(user_pref_values[0])
    vectorizer = TfidfVectorizer(vocabulary=vocab, lowercase=False, tokenizer=tokenize)
    vectors = vectorizer.fit_transform(user_pref_values).toarray()
    words = vectorizer.get_feature_names()
    # idf = vectorizer.idf_
    # print dict(zip(vectorizer.get_feature_names(), idf))
    return words, vectors

def build_usr_pref(categories):
    # global user_pref_level2
    # global user_pref_level1
    user_pref_level2 = {}
    user_pref_level1 = {}
    if not any(user_pref_level1):
        usrs = users_df['User_ID'].unique()
        for usr_id in usrs:
            catids = (users_df[users_df['User_ID']==usr_id])['Category_ID'].values
            user_pref_level2[usr_id] = categoryid_to_doc(list(catids), categories)
            user_pref_level1[usr_id] = categoryid_to_doc(list(catids), categories, level=1)
    return OrderedDict(user_pref_level1), OrderedDict(user_pref_level2)

def user_venue_scores(usr_location_matrix):
    M = usr_location_matrix.as_matrix()
    user_hub__initial_score = usr_location_matrix.sum(axis=1).values
    user_hub_score = power_method.power_method(np.dot(M, M.T), user_hub__initial_score, 10)

    venue_auth_initial_score = usr_location_matrix.sum(axis=0).values
    venue_hub_score = power_method.power_method(np.dot(M.T, M), venue_auth_initial_score, 10)

    return user_hub_score, venue_hub_score


def user_venue_scores_by_category_precompute(sub_categories):
    usr_location_matrix, users_index = build_usrlocation_matrix(sub_categories)
    user_hub_score, venue_hub_score = user_venue_scores(usr_location_matrix)
    return user_hub_score, venue_hub_score, users_index, usr_location_matrix

def user_venue_scores_by_venue_precompute(cat_id):
    usr_location_matrix, users_index = build_usrlocation_matrix_by_venues(cat_id)
    user_hub_score, venue_hub_score = user_venue_scores(usr_location_matrix)
    return user_hub_score, venue_hub_score, users_index, usr_location_matrix

def user_venue_scores_by_category(key):
    if city != 'LA':
        user_hub_score = np.load('../pre_500/scores/'+key+'_nyc_user_hub_score.npy')
        venue_hub_score = np.load('../pre_500/scores/'+key+'_nyc_venue_hub_score.npy')
        users_index = np.load('../pre_500/scores/'+key+'_nyc_users_index.npy')
        usr_location_matrix = np.load('../pre_500/scores/'+ key+"_nyc_users_location_matrix.npy")
    else:
        user_hub_score = np.load('../pre_500/scores/'+key+'_user_hub_score.npy')
        venue_hub_score = np.load('../pre_500/scores/'+key+'_venue_hub_score.npy')
        users_index = np.load('../pre_500/scores/'+key+'_users_index.npy')
        usr_location_matrix = np.load('../pre_500/scores/'+ key+"_users_location_matrix.npy")
    return user_hub_score, venue_hub_score, users_index, usr_location_matrix

def user_venue_scores_by_venue(key):
    if city != 'LA':
        user_hub_score = np.load('../pre_500/scores/'+key+'_nyc_user_hub_score.npy')
        venue_hub_score = np.load('../pre_500/scores/'+key+'_nyc_venue_hub_score.npy')
        users_index = np.load('../pre_500/scores/'+key+'_nyc_users_index.npy')
        usr_location_matrix = np.load('../pre_500/scores/'+ key+"_nyc_users_location_matrix.npy")
    else:
        user_hub_score = np.load('../pre_500/scores/'+key+'_user_hub_score.npy')
        venue_hub_score = np.load('../pre_500/scores/'+key+'_venue_hub_score.npy')
        users_index = np.load('../pre_500/scores/'+key+'_users_index.npy')
        usr_location_matrix = np.load('../pre_500/scores/'+ key+"_users_location_matrix.npy")
    return user_hub_score, venue_hub_score, users_index, usr_location_matrix

def build_usr_personal_pref_hierarchy():
    high_level_cat = cat.get_categories()
    user_pref_level1, user_pref_level2 = \
                                build_usr_pref(high_level_cat)
    words_level_1, vectors_level1 = \
        get_peronalpreference_vectors(high_level_cat.keys(), user_pref_level1.values())
    words_level_2, vectors_level2 = \
        get_peronalpreference_vectors(cat.get_sub_categories_names(high_level_cat), \
                                                        user_pref_level2.values())
    return words_level_1, vectors_level1, words_level_2, vectors_level2



if __name__=='__main__':
    load_users_tips()
    load_users()
