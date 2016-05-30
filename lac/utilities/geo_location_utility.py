# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid import renderers

from dace.objectofcollaboration.principal.util import get_current

from lac.views.filter import find_entities


def get_geo_cultural_event(request, filters={}, user=None):
    if user is None:
        user = get_current()

    objects = find_entities(
        user=user,
        # ignore_end_date=True,
        include_site=True,
        **filters)
    locations = {}
    for obj in objects:
        schedules = obj.substitutions
        for schedule in schedules:
            coordinates = schedule.venue.addresses[0].get(
                'coordinates', None) if schedule.venue else None
            if coordinates:
                sections = obj.sections
                coordinates = coordinates.split(',')
                data = {}
                data['latitude'] = coordinates[0]
                data['longitude'] = coordinates[1]
                data['coordinates'] = coordinates
                data['icon'] = 'lacstatic/images/map/marker_blue.png'
                data['title'] = obj.title
                data['url'] = request.resource_url(obj, '@@index')
                data['content'] = renderers.render(
                    obj.templates.get('map'),
                    {'object': obj,
                     'schedule': schedule
                    },
                    request)
                data['show'] = False
                sections.append('all')
                data['categories'] = sections
                locations[str(schedule.object_id)] = data

    return locations
