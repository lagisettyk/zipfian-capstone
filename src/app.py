import venues
import users
import categories
import candidate_selection as cs
from collections import OrderedDict

def load_data():
    categories.load_categories()
    venues.load_venues()
    users.load_users_tips()

def candidate_suggestions(sr, usr_index):
    venue_list = venues.get_venues_sp_range(sr)
    user_list = users.get_visited_users(venue_list)
    words_level_1, vectors_level1, words_level_2, vectors_level2 = \
                            users.build_usr_personal_pref_hierarchy()
    u_wch = [(list(words_level_2),list(vectors_level2[usr_index])),
                 (list(words_level_1), list(vectors_level1[usr_index]))]
    candidate_venues, expert_users = \
                        cs.candidate_selection(sr, u_wch, 10)
    return candidate_venues, expert_users

def similar_users_rankorder(user_id, expert_users):
    pass


if __name__=='__main__':
    load_data()
    sr = venues.SpatialRange(33.7482354, -118.4071307, 20.0)
    # candidate_venues, expert_users = candidate_suggestions(sr, 9846876)
    candidate_venues, expert_users = candidate_suggestions(sr, 27)
    print candidate_venues, expert_users
    suggest_df = venues.get_venues_by_id(candidate_venues)
