import pandas as pd
from spatial_range import distance_on_unit_sphere

venues_df = None

class SpatialRange(object):
    def __init__(self, lat, lon, dist):
        self._latitude = lat
        self._longitude = lon
        self._distance = dist

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def distance(self):
        return self._distance


def load_venues():
    global venues_df
    venues = []
    with open('../data/Venues/LA/LA-Venues.txt') as f:
        for line in f:
            venues.append(line.strip().split('\t')[:14])
    df = pd.DataFrame(venues)
    cols = ['Venue_id', 'Venue_name', 'latitude', 'longitude', \
     'address', 'city', 'state', 'checkin_#', 'checked_user#', 'current_user#',\
     'todo#', 'category_#',  'category_id0', 'category_id1']
    df.columns = cols
    df['Venue_id'] = df['Venue_id'].apply(lambda x: str(x).strip('\"'))
    df['category_id1'] = df['category_id1'].apply(lambda x: str(x).strip('\"'))
    venues_df = df

def get_venues_by_id(venue_list):
    return venues_df[venues_df['Venue_id'].isin(venue_list)]

def get_venues_sp_range(sr, falg=True):
    venue_list = []
    lat_long = \
    zip(list(venues_df['Venue_id'].values), \
     list(venues_df['latitude'].values), list(venues_df['longitude'].values))
    for location in lat_long:
        distance = distance_on_unit_sphere(sr.latitude, sr.longitude, float(location[1]), float(location[2]))
        if distance <= sr.distance:
            venue_list.append(location[0])
    return venue_list


if __name__=='__main__':
    load_venues()
