import numpy as np
import users
import categories as cat
from collections import defaultdict
import time

def cosine_similarity(vec1, vec2):
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    norm_prod = norm1 * norm2
    return vec1.T.dot(vec2) / norm_prod

def similar_users_rankorder_bycosine(user_id, expert_users):
    similar_users = []
    high_level_cat = cat.get_categories()
    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    words_level_1, vectors_level1, words_level_2, vectors_level2 = \
                            users.build_usr_personal_pref_hierarchy()
    vect1 = vectors_level1[user_pref_level1.keys().index(user_id)]
    for expert in expert_users:
        vect2 = vectors_level1[user_pref_level1.keys().index(expert)]
        similar_users.append((expert, cosine_similarity(vect1, vect2)))
    return sorted(similar_users, key=lambda x: x[1], reverse=True)

def level_similarity(user_id, expert_users, user_pref_level, vectors_level):
    ls_users = defaultdict(int)
    vect1 = vectors_level[user_pref_level.keys().index(user_id)]
    for expert in expert_users:
        vect2 = vectors_level[user_pref_level.keys().index(expert)]
        level_sim = np.sum(np.minimum(vect1, vect2))
        ls_users[expert] = level_sim
    return ls_users

def entropy_by_level1(usrs):
    entropy = defaultdict(int)
    high_level_cat = cat.get_categories()
    for key in high_level_cat.keys():
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                                        users.user_venue_scores_by_category(key)
        for usr in usrs:
            index = np.flatnonzero(users_index==usr)
            if len(index) == 1:
                entropy[usr] += user_hub_score[index][0]
    return entropy

def entropy_by_level2(usrs):
    entropy = defaultdict(int)
    high_level_cat = cat.get_categories()
    sub_dict = cat.get_sub_categories_id_dict(high_level_cat)
    for key in sub_dict.keys():
        user_hub_score, venue_hub_score, users_index, usr_location_matrix = \
                                        users.user_venue_scores_by_venue(key)
        for usr in usrs:
            index = np.flatnonzero(users_index==usr)
            if len(index) == 1:
                entropy[usr] += user_hub_score[index][0]
    return entropy


def similar_users_rankorder(user_id, expert_users):
    similar_users = []
    high_level_cat = cat.get_categories()


    user_pref_level1, user_pref_level2 = \
                                    users.build_usr_pref(high_level_cat)
    words_level_1, vectors_level1, words_level_2, vectors_level2 = \
                            users.build_usr_personal_pref_hierarchy()

    ls_users_level1 = \
      level_similarity(user_id, expert_users, user_pref_level1, vectors_level1)
    ls_users_level2 = \
      level_similarity(user_id, expert_users, user_pref_level2, vectors_level2)

    usrs = expert_users
    usrs.add(user_id)

    start = time.time()
    entropy_level_1 = entropy_by_level1(usrs)
    entropy_level_2 = entropy_by_level2(usrs)
    end = time.time()
    print "Time taken for computing entropy levels: ", end - start

    usr_entropy_level1 = entropy_level_1[user_id]
    usr_entropy_level2 = entropy_level_2[user_id]



    for expert in expert_users:
        score1 = \
            ls_users_level1[expert] / (1+abs(-usr_entropy_level1 + entropy_level_1[expert]))
        score2 = \
             2 * (ls_users_level2[expert] / (1+abs(-usr_entropy_level2 + entropy_level_2[expert])))
        similar_users.append((expert, score1+score2))
    return similar_users

if __name__ == "__main__":
    cat.load_categories()
    experts = []
    entropy_by_level(experts)
