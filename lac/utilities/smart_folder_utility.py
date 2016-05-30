# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from dace.objectofcollaboration.principal.util import Anonymous

from lac import CLASSIFICATIONS
from lac.views.filter import (
    get_site_filter, find_entities, FilterSchema)
from lac.views.filter.util import (
    get_filter_nodes_to_omit, and_op)
from lac.utilities.utils import (
    get_site_folder, deepcopy)


def _has_artists_field(content_types):
    types_with_artists = ['cultural_event', 'review',
                          'cinema_review', 'film_synopses']
    return any(ctype in types_with_artists for ctype in content_types)


def get_adapted_filter(folder, user):
    # site = get_site_folder(True)
    # site_filters = get_site_filter(site)
    is_anonymous = isinstance(user, Anonymous)
    result = {'select': ['metadata_filter', 'geographic_filter',
                         'contribution_filter', 'temporal_filter',
                         'text_filter', 'other_filter']}
    if is_anonymous:
        result = {
            'select': [('metadata_filter', ['negation', 'content_types', 'tree']),
                       'geographic_filter',
                       'contribution_filter',
                       'temporal_filter', 'text_filter']}
    # folder_filters = getattr(folder, 'filters', [])
    # if folder_filters:
    #     #TODO filters intersection
    #     omit = get_filter_nodes_to_omit(FilterSchema(), folder_filters[0])
    #     if omit:
    #         result = {'omit': omit}
    return result


def interface_in(other_interface, interfaces):
    for interface in interfaces:
        if other_interface.isOrExtends(interface):
            return True

    return False


def get_folder_content(folder, user,
                       add_query=None,
                       sort_on='release_date', reverse=True,
                       **args):
    _filters = deepcopy(getattr(folder, 'filters', []))
    # retrieve classifications queries
    classifications = [CLASSIFICATIONS[fid] for fid
                       in getattr(folder, 'classifications', [])]
    query = None
    if classifications:
        for classification in classifications:
            classification_query = classification().get_query(**args)
            query = and_op(query, classification_query)

    query = and_op(query, add_query)
    objects = find_entities(user=user,
                            add_query=query,
                            sort_on=sort_on, reverse=reverse,
                            filters=_filters,
                            include_site=True,
                            filter_op='or',
                            **args)
    return objects
