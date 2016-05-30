# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from dace.util import find_catalog
from dace.objectofcollaboration.principal.util import (
    get_current)

from lac.content.interface import (
    IVenue, IArtistInformationSheet)
from lac.views.filter import get_entities_by_title
from lac.utilities.memoize import request_memoize
from lac.views.filter import find_entities
from lac.utilities.ical_date_utility import get_dates_intervals
from lac.fr_lexicon import normalize_title


def get_time_filter(l_time):

    def filter_op(time):
        for time_ in l_time:
            t1start = time_['start']
            t2start = time['start']
            t1end = time_['end']
            t2end = time['end']
            if t2start <= t1start <= t2end or\
               t1start <= t2start <= t1end:
                return True

        return False

    return filter_op


def conflict_times(time1, time2):
    if not time1 or not time2:
        return True

    for time in filter(get_time_filter(time1), time2):
        return True

    return False


def conflict_schedules(schedule1, schedule2):
    venue1 = schedule1.venue
    venue2 = schedule2.venue
    if venue1 is None or venue2 is None:
        return False

    same_venue = venue1 is venue2 or venue1.eq(venue2) or \
                 venue2 in list(get_venue_duplicates(venue1))
    has_conflict = False
    if same_venue:
        dates1 = get_dates_intervals(schedule1, schedule1.dates_dates_str)
        dates2 = get_dates_intervals(schedule2, schedule2.dates_dates_str)
        dates1_keys = list(dates1.keys())
        common_dates = filter(lambda x: x in dates2, dates1_keys)
        conflict_dates = filter(lambda x: conflict_times(dates1[x], dates2[x]), common_dates)
        for time in conflict_dates:
            has_conflict = True
            break

    return same_venue and has_conflict


def get_schedules_filter(schedules):

    def filter_op(event):
        for schedule in event.schedules:
            for o_schedule in schedules:
                if conflict_schedules(schedule, o_schedule):
                    return True

        return False

    return filter_op


@request_memoize
def find_duplicates_cultural_events(obj, state=()):
    user = get_current()
    title = getattr(obj, 'title', None)
    lac_catalog = find_catalog('lac')
    #index
    title_index = lac_catalog['object_title']
    #query
    title = normalize_title(title)
    query = title_index.eq(title)
    result = find_entities(
        user=user,
        metadata_filter={'content_types': ['cultural_event'],
                         'states': state},
        add_query=query,
        include_site=True)
    events = [o for o in result.all() if o is not obj
              and o is not obj.original
              and o not in obj.branches]
    events = filter(get_schedules_filter(obj.schedules), events)
    return list(events)


@request_memoize
def find_duplicates_artist(obj, state=()):
    original = obj.original
    objects = [o for o in get_entities_by_title(
              [IArtistInformationSheet], obj.title,
               metadata_filter={'states': state})
               if o not in (obj, original) and
               o not in obj.branches]
    return objects


@request_memoize
def get_venue_duplicates(obj, state=()):
    duplicates = get_entities_by_title([IVenue],
                                       obj.title,
                                       metadata_filter={'states': state})
    duplicates = [v for v in duplicates
                  if getattr(v, 'addresses', []) and
                  (list(filter(lambda z: z in obj.zipcodes, v.zipcodes)) or
                  v.city == obj.city)]
    return duplicates


@request_memoize
def find_duplicates_venue(obj, state=()):
    original = obj.original
    duplicates = get_venue_duplicates(obj, state)
    objects = [o for o in duplicates
               if o not in (obj, original) and
               o not in obj.branches]
    return objects
