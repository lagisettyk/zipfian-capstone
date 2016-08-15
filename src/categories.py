import pandas as pd
import json
from collections import defaultdict

data = None
categories = {}
def load_categories():
    global data
    with open('../pre_500/categories.txt') as f:
        json_str = f.read()
    data = json.loads(unicode(json_str, "ISO-8859-1"))['response']

def get_categories():
    global categories
    if not any(categories):
        cat_hierachy = {x['name']:x for x in data['categories']}
        for key, value in cat_hierachy.iteritems():
            categories[key] = value
    return categories

def get_sub_categories_by_category(cat, key):
    sub_categories = set()
    for c in cat[key]['categories']:
        sub_categories.add(c['name'])
    return sub_categories

def get_sub_categories_names(cat):
    sub_categories = set()
    for key in cat.keys():
        for c in cat[key]['categories']:
            sub_categories.add(c['name'])
    return sub_categories

def get_sub_categories_names_dict(cat):
    sub_categories = defaultdict()
    for key in cat.keys():
        for c in cat[key]['categories']:
            sub_categories[c['name']] = key
    return sub_categories

def get_sub_categories_id_dict(cat):
    sub_categories = defaultdict()
    for key in cat.keys():
        for c in cat[key]['categories']:
            sub_categories[c['name']] = c['id']
    return sub_categories

def get_sub_category_ids(category):
    ids = []
    for cat in category:
        ids.append(cat['id'])
    return ids
