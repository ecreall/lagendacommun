# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from persistent.list import PersistentList

from dace.util import getSite


def merge_artists(artists):
    root = getSite()
    new_artists = []
    from lac.utilities.duplicates_utility import (
        find_duplicates_artist)
    for artist in artists:
        old_artists = find_duplicates_artist(artist)
        published_old_artists = [a for a in old_artists
                                 if 'published' in a.state]
        if old_artists:
            old_artist = published_old_artists[0] if \
                published_old_artists else old_artists[0]
            new_artists.append(old_artist)
        else:
            new_artists.append(artist)
            artist.state = PersistentList(['editable'])
            root.addtoproperty('artists', artist)
            artist.reindex()
            import transaction
            transaction.commit()

    return new_artists


def merge_venues(venues):
    root = getSite()
    new_venues = []
    from lac.utilities.duplicates_utility import (
        find_duplicates_venue)
    for venue in venues:
        if not venue.title.strip():
            addresses = getattr(venue, 'addresses', [])
            venue.title = addresses[0].get('address', 'None') \
                if addresses else 'None'

        old_venues = find_duplicates_venue(venue)
        published_old_venues = [a for a in old_venues
                                if 'published' in a.state]
        if old_venues:
            old_venue = published_old_venues[0] if \
                published_old_venues else old_venues[0]
            new_venues.append(old_venue)
        else:
            new_venues.append(venue)
            venue.state = PersistentList(['editable'])
            root.addtoproperty('venues', venue)
            venue.reindex()
            import transaction
            transaction.commit()

    return new_venues
