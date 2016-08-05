import venues
import users
import categories
import candidate_selection as cs

def load_data():
    categories.load_categories()
    venues.load_venues()
    users.load_users_tips()


if __name__=='__main__':
    load_data()
    sr = venues.SpatialRange(33.7482354, -118.4071307, 20.0)
    venue_list = venues.get_venues_sp_range(sr)
    user_list = users.get_visited_users(venue_list)
    print len(user_list), user_list

    high_level_cat = categories.get_categories()
    user_pref_level1, user_pref_level2, usrs = \
                                users.build_usr_pref(high_level_cat)
    words_level_1, vectors_level1 = \
        users.get_peronalpreference_vectors(high_level_cat.keys(), user_pref_level1.values())
    words_level_2, vectors_level2 = \
    users.get_peronalpreference_vectors(categories.get_sub_categories_names(high_level_cat), \
                                                        user_pref_level2.values())

    u_wch = [(list(words_level_2),list(vectors_level2[999])),
                 (list(words_level_1), list(vectors_level1[999]))]

    candidate_venues, expert_users = \
                        cs.candidate_selection(sr, u_wch, 5)
    print candidate_venues, expert_users
    suggest_df = venues.get_venues_by_id(candidate_venues)
