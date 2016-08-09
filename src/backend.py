import venues
import users
import categories
import candidate_selection as cs
import location_rating_inference as lr
from collections import OrderedDict
from sklearn.metrics import pairwise_distances
import numpy as np

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

def run():
    load_data()
    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    usr_index = 27
    user_id = user_pref_level1.keys()[usr_index]
    sr = venues.SpatialRange(33.842623, -118.288384079933, 8.0)
    candidate_venues, expert_users, candidates_per_expert = \
                                    candidate_suggestions(sr, usr_index, k=10)
    # print candidate_venues, expert_users, candidates_per_expert
    #similar_users = lr.similar_users_rankorder_bycosine(user_id, expert_users)
    similar_users = lr.similar_users_rankorder(user_id, expert_users)
    suggestions = \
        final_candidates(candidates_per_expert, similar_users, user_id, k=5)
    suggest_df = venues.get_venues_by_id(suggestions)
    return suggest_df


if __name__=='__main__':
    load_data()
    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    usr_index = 27
    user_id = user_pref_level1.keys()[usr_index]
    sr = venues.SpatialRange(33.842623, -118.288384079933, 8.0)
    candidate_venues, expert_users, candidates_per_expert = \
                                    candidate_suggestions(sr, usr_index, k=10)
    # print candidate_venues, expert_users, candidates_per_expert
    #similar_users = lr.similar_users_rankorder_bycosine(user_id, expert_users)
    similar_users = lr.similar_users_rankorder(user_id, expert_users)
    suggestions = \
        final_candidates(candidates_per_expert, similar_users, user_id, k=5)
    suggest_df = venues.get_venues_by_id(suggestions)
    print user_id, suggest_df
