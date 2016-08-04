import pandas as pd
import numpy as np
import power_method
from sklearn.feature_extraction.text import TfidfVectorizer

users_df = None

def load_users_tips():
    global users_df
    users_df = pd.read_csv('../data/Tips/LA/LA-User-Tips.csv')

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

def categoryid_to_doc(catids, categories, level=2):
    usr_category_doc = ''
    for key in categories.keys():
        for cat in categories[key]['categories']:
            if cat['id'] in catids:
                if level == 2:
                    # usr_category_doc += cat['name'].replace (" ", "_") + ' '
                    usr_category_doc += cat['name'] + ' '
                else:
                    #  usr_category_doc += str(hash(key)) + ' '
                    usr_category_doc += key + ' '
    return usr_category_doc

def get_peronalpreference_vectors(vocab, user_pref_values):
    vectorizer = TfidfVectorizer(vocabulary=vocab, lowercase=False)
    vectors = vectorizer.fit_transform(user_pref_values).toarray()
    words = vectorizer.get_feature_names()
    # idf = vectorizer.idf_
    # print dict(zip(vectorizer.get_feature_names(), idf))
    return words, vectors

def build_usr_pref(categories):
    user_pref_level2 = {}
    user_pref_level1 = {}
    users = users_df['User_ID'].unique()
    for usr_id in users:
        catids = (users_df[users_df['User_ID']==usr_id])['Category_ID'].values
        user_pref_level2[usr_id] = categoryid_to_doc(list(catids), categories)
        user_pref_level1[usr_id] = categoryid_to_doc(list(catids), categories, level=1)
    return user_pref_level1, user_pref_level2

def user_venue_scores(sub_categories):
    usr_location_matrix, users_index = build_usrlocation_matrix(sub_categories)
    M = usr_location_matrix.as_matrix()
    user_hub__initial_score = usr_location_matrix.sum(axis=1).values
    user_hub_score = power_method.power_method(np.dot(M, M.T), user_hub__initial_score, 100)

    venue_auth_initial_score = usr_location_matrix.sum(axis=0).values
    venue_hub_score = power_method.power_method(np.dot(M.T, M), venue_auth_initial_score, 100)

    return user_hub_score, venue_hub_score, users_index



if __name__=='__main__':
    load_users_tips()
