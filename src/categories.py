import pandas as pd
import json
from collections import defaultdict

data = None
def load_categories():
    global data
    with open('../data/categories.txt') as f:
        json_str = f.read()
    data = json.loads(unicode(json_str, "ISO-8859-1"))['response']

def get_categories():
    categories = {}
    cat_hierachy = {x['name']:x for x in data['categories']}
    for key, value in cat_hierachy.iteritems():
        categories[key] = value
    return categories

def get_sub_categories_names(categories):
    sub_categories = set()
    for key in categories.keys():
        for cat in categories[key]['categories']:
            sub_categories.add(cat['name'])
    return sub_categories

def get_sub_categories_names_dict(categories):
    sub_categories = defaultdict()
    for key in categories.keys():
        for cat in categories[key]['categories']:
            sub_categories[cat['name']] = key
    return sub_categories

def get_sub_category_ids(category):
    ids = []
    for cat in category:
        ids.append(cat['id'])
    return ids
