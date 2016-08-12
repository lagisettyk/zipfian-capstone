import venues
import users
import categories
import candidate_selection as cs
import location_rating_inference as lr
from collections import OrderedDict
from sklearn.metrics import pairwise_distances
import numpy as np
from timeit import Timer
import time
from collections import Counter
from collections import defaultdict

### AIzaSyBTT8YSKGtJV9ZVcoVEqHUJuLCLPqXXAto ### Google Maps API key...

def load_data():
    categories.load_categories()
    venues.load_venues()
    users.load_users_tips()

def candidate_suggestions(sr, usr_index, k):
    venue_list = venues.get_venues_sp_range(sr)
    user_list = users.get_visited_users(venue_list)
    words_level_1, vectors_level1, words_level_2, vectors_level2 = \
                            users.build_usr_personal_pref_hierarchy()
    u_wch = [(list(words_level_2),list(vectors_level2[usr_index])),
                 (list(words_level_1), list(vectors_level1[usr_index]))]
    candidate_venues, expert_users, candidates_per_expert  = \
                        cs.candidate_selection(sr, u_wch, k)
    return candidate_venues, expert_users, candidates_per_expert

def final_candidates(candidates_per_expert, similar_users, user_id, k):
    final_candidates = []
    for index, similar_user in enumerate(similar_users):
        if index == 0 and similar_user[0] == user_id:
            continue
        final_candidates.extend(candidates_per_expert[similar_user[0]])
        if len(final_candidates) >= k:
            break
    return final_candidates

def venue_density(latitude=33.842623, longitude=-118.288384079933):
    sr = venues.SpatialRange(latitude, longitude, 8.0)
    venue_list = venues.get_venues_sp_range(sr)
    venues_df = venues.get_venues_by_id(venue_list)
    return venues_df

def run(latitude=33.842623, longitude=-118.288384079933, userid=99):
    #load_data()
    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    usr_index = userid
    user_id = user_pref_level1.keys()[usr_index]
    # usr_location_map = \
    # getUsrLocationMap(user_pref_level1, user_pref_level2, high_level_cat, user_id)
    sr = venues.SpatialRange(latitude, longitude, 8.0)

    start = time.time()
    candidate_venues, expert_users, candidates_per_expert = \
                                    candidate_suggestions(sr, usr_index, k=8)
    end = time.time()
    print "Predicting candidate recommendations step: ", end - start
    # print candidate_venues, expert_users, candidates_per_expert
    # similar_users = lr.similar_users_rankorder_bycosine(user_id, expert_users)
    start = time.time()
    similar_users = lr.similar_users_rankorder(user_id, expert_users)
    end = time.time()
    print "Finding similar users step: ", end - start

    start = time.time()
    suggestions = \
        final_candidates(candidates_per_expert, similar_users, user_id, k=5)
    suggest_df = venues.get_venues_by_id(suggestions)
    end = time.time()
    print "Final suggestions step: ", end - start

    return suggest_df, (dict(similar_users)).keys()[0:3]

#def getUsrLocationMap(user_pref_level1, user_pref_level2, high_level_cat, user_id):
def getUsrLocationMapById(latitude, longitude, user_id):

    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    locationDict = {}
    level_1 = user_pref_level1[user_id]
    if level_1:
        level_2 = user_pref_level2[user_id]
        counter_level1 = Counter(level_1.rstrip('||').split('||'))
        counter_level2 = Counter(level_2.rstrip('||').split('||'))


        locationDict["name"] = "Top Level: " + str(len(level_1.rstrip('||').split('||')))
        locationDict["parent"] = "null"
        locationDict["children"] = []
        for key, value in counter_level1.iteritems():
            sub_categories = \
                    categories.get_sub_categories_by_category(high_level_cat, key)
            filterd_sub_categories =  \
                 [elem for elem in sub_categories if elem in counter_level2.keys()]

            sub_children_dict =\
            [{"name": filtered_cat + ": " + str(counter_level2[filtered_cat]), "parent":key} \
            for filtered_cat in filterd_sub_categories]
            locationDict["children"].append({"name": key + " : " + str(value),\
                "parent": locationDict["name"], "children": sub_children_dict})
    return locationDict

def getUsrLocationMap(latitude=33.842623, longitude=-118.288384079933, usr_index=45):
    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    user_id = user_pref_level1.keys()[usr_index]
    return getUsrLocationMapById(latitude, longitude, user_id)



if __name__=='__main__':
    load_data()
    suggest_df, similar_users = run()
    locationMap = getUsrLocationMap()
    #venue_list = venue_density()
    # t = Timer(lambda: run())
    # print "Completed recommendation in %s seconds." % t.timeit(1)
    #locationMap = getUsrLocationMap()
    # load_data()
    # high_level_cat = categories.get_categories()
    # user_pref_level1, user_pref_level2 = \
    #                                 users.build_usr_pref(high_level_cat)
    # usr_index = 27
    # user_id = user_pref_level1.keys()[usr_index]
    # sr = venues.SpatialRange(33.842623, -118.288384079933, 8.0)
    # candidate_venues, expert_users, candidates_per_expert = \
    #                                 candidate_suggestions(sr, usr_index, k=10)
    # similar_users = lr.similar_users_rankorder(user_id, expert_users)
    # suggestions = \
    #     final_candidates(candidates_per_expert, similar_users, user_id, k=5)
    # suggest_df = venues.get_venues_by_id(suggestions)
    # print user_id, suggest_df
