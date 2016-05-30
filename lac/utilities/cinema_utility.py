# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
from persistent.list import PersistentList

from dace.util import find_catalog

from lac.views.filter import find_entities
from lac.content.interface import IFilmSchedule
from lac.content.film_schedule import FilmSchedule
from lac import log


FR_MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
          'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def dates_to_fr_date(date_au, date_du=None):
    if not date_du:
        date_du = datetime.datetime.now()

    current_year = datetime.datetime.now().year
    date_year = date_au.year
    year = ((current_year != date_year) and date_year) or ''
    au_date_str = '{day} {month}{year}'.format(**{
        'day': str(date_au.day),
        'month': FR_MONTHS[date_au.month-1],
        'year': ((year and (' '+str(year))) or '')})

    date_du_year = date_du.year
    year = ((current_year != date_du_year) and date_du_year) or ''
    du_date_str = '{day} {month}{year}'.format(**{
        'day': str(date_au.day),
        'month': FR_MONTHS[date_au.month-1],
        'year': ((year and (' '+str(year))) or '')})

    return 'Du {du_date} au {au_date}'.format(**{
        'du_date': du_date_str,
        'au_date': au_date_str
        })


def next_weekday(d, weekday, weeknb=0):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:# Target day already happened this week
        days_ahead += 7
        if weeknb > 0:
            weeknb = weeknb - 1

    return d + datetime.timedelta(days_ahead+(weeknb*7))


def get_cineam_schedules(cinema=None):
    query = None
    if cinema:
        lac_index = find_catalog('lac')
        object_venue_index = lac_index['object_venue']
        query = object_venue_index.any([cinema.get_id()])

    film_schedules = find_entities(
        interfaces=[IFilmSchedule],
        metadata_filter={'states': ['published']},
        include_site=True,
        sort_on='release_date',
        reverse=True,
        add_query=query)
    result = {}
    for film_schedule in film_schedules:
        if getattr(film_schedule, 'venue', None):
            if film_schedule.venue in result:
                result[film_schedule.venue].append(film_schedule)
            else:
                result[film_schedule.venue] = [film_schedule]

    return result


def get_cinema_venues_data(cinema=None):
    schedules = get_cineam_schedules(cinema)
    result = {}
    for venue, film_schedules in schedules.items():
        if film_schedules:
            venue = film_schedules[0].venue
            venue_data = {'id': venue.get_id(),
                          'title': venue,
                          'schedules': "\n\n".join([f.title + "\n" + getattr(f, 'description', '')
                                                    for f in film_schedules])}
            result[venue] = venue_data

    return result


def get_schedules(schedules_str, venue, dates):
    lines = schedules_str.replace('\r', '').split('\n')
    lines.append('')
    schedules_data = []
    schedules = []
    schedule = []
    for line in lines:
        if line:
            schedule.append(line)
        else:
            if schedule:
                schedules_data.append(schedule)
                schedule = []

    #Preserve order
    schedules_data.reverse()
    for schedule in schedules_data:
        try:
            obj = FilmSchedule(title=schedule[0],
                               description='\n'.join(schedule[1:]),
                               dates=dates)
            obj.setproperty('venue', venue)
            obj.state = PersistentList(['published'])
            schedules.append(obj)
        except Exception as error:
            log.warning(error)

    return schedules
