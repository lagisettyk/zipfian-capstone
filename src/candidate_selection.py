import venues
import users
import numpy as np
import categories as cat

def top_experts(k, U, ct):

    high_level = cat.get_categories()
    sub_dict = cat.get_sub_categories_id_dict(high_level)
    if ct in sub_dict:
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                users.user_venue_scores_by_venue(ct)
    else:
        high_level_category = ct
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                        users.user_venue_scores_by_category(high_level_category)
    index =  np.argsort(-user_hub_score)
    expert_users = []
    for i in index:
        if users_index[i] in U and len(expert_users) < round(k):
            expert_users.append(users_index[i])
    return expert_users


def matched_venues(expert, venue_list):
    matched_venues = []
    usr_venues = users.get_venues_filered_by_users([expert])
    for ven in usr_venues:
        if ven in venue_list:
            matched_venues.append(ven)
    return matched_venues

def candidate_selection(sr, u_wch, N):
    '''
    Inputs: Spatial Region R, A users.w.c.h, N # of recommendations
    Output: A set of local experts, set of candidate venues/locations
    '''
    candidate_venues = set()
    expert_users = set()
    candidates_per_expert = {}
    #Step 1 Retrieve venues V'
    venue_list = venues.get_venues_sp_range(sr)
    users_list = users.get_visited_users(venue_list)

    while True:
        for level in xrange(len(u_wch)):
            ### Iterating over tuples... of word vector and tfidf vectors...
            tfidfVector = u_wch[level][1]
            tfidfVector = np.array(tfidfVector)
            w_min = np.min(tfidfVector[np.nonzero(tfidfVector)]) ##########**********Need to fix this one
            for index, ct in enumerate(u_wch[level][0]):
                if u_wch[level][1][index]!= 0.0:
                    k = u_wch[level][1][index]/w_min ##Caluclate no of users
                    expert_temp = top_experts(k, users_list, ct)

                    for expert in expert_temp:
                        v = matched_venues(expert, venue_list)
                        if len(v) >= 1:
                            candidate_venues.update(v)
                            expert_users.add(expert)
                            candidates_per_expert[expert] = v
            if len(candidate_venues) >= N or len(expert_users) == len(users_list):
                return candidate_venues, expert_users, candidates_per_expert
