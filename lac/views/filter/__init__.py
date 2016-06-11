# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import re
import colander
import datetime
import pytz
import types
import json
from hypatia.text.parsetree import ParseError
from hypatia.util import ResultSet
from hypatia.query import Not
from pyramid.view import view_config
from pyramid import renderers
from pyramid.threadlocal import (
    get_current_registry, get_current_request)

from hypatia.query import Any

from substanced.util import get_oid

from dace.util import getSite, find_catalog, get_obj
from dace.objectofcollaboration.principal.util import (
    get_current, has_any_roles)
from pontus.widget import (
    Select2Widget, AjaxSelect2Widget, SimpleMappingWidget)
from pontus.schema import Schema, omit, select
from pontus.form import FormView
from deform_treepy.widget import (
    DictSchemaType, KeywordsTreeWidget)
from deform_treepy.utilities.tree_utility import (
    get_branches)

from lac import _
from lac import core
from lac.content.processes import STATES_MEMBER_MAPPING
from lac.content.keyword import (
    DEFAULT_TREE, DEFAULT_TREE_LEN)
from lac.utilities.utils import (
    get_site_folder)
from lac.views.filter.util import (
    match_in, get_zipcodes, get_zipcodes_from_cities,
    get_site_filter, deepcopy, get_node_query,
    get_filters_query, QUERY_OPERATORS, and_op, get_analyzed_data,
    merge_with_filter_view)
from lac.views.widget import SimpleMappingtWidget
from lac import log
from lac.content.interface import IAlert
from lac.fr_lexicon import normalize_title

# monkey patch query optimizers
import lac.views.filter.query_optimization

#If updated: See data_manager utility FILTER_DEFAULT_DATA


FILTER_SOURCES = {}


FILTER_TEMPLATES = {
    'geographic_filter': {
        'default': 'lac:views/filter/templates/geographic_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/geographic_filter.pt'
    },
    'metadata_filter': {
        'default': 'lac:views/filter/templates/metadata_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/metadata_filter.pt'
    },
    'contribution_filter': {
        'default': 'lac:views/filter/templates/contribution_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/contribution_filter.pt'
    },
    'text_filter': {
        'default': 'lac:views/filter/templates/text_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/text_filter.pt'
    },
    'temporal_filter': {
        'default': 'lac:views/filter/templates/temporal_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/temporal_filter.pt'
    },
    'other_filter': {
        'default': 'lac:views/filter/templates/other_filter.pt',
        'extraction': 'lac:views/filter/templates/extraction/other_filter.pt'
    },
    'filter': {
        'default': 'lac:views/filter/templates/filter_template.pt',
        'extraction': 'lac:views/filter/templates/extraction/filter_template.pt'
    },
    'global': {
        'default': 'lac:views/filter/templates/global.pt',
        'extraction': 'lac:views/filter/templates/extraction/global.pt'
    }
}


_marker = object()

#**********************************************Filter queries getters


def content_types_query(node, **args):
    value = None
    if 'metadata_filter' in args:
        value = args['metadata_filter']

    content_types = value.get('content_types', []) if value else []
    if not content_types:
        content_types = list(core.SEARCHABLE_CONTENTS.keys())

    if args.get('interfaces', []):
        interfaces = [i.__identifier__ for i in args['interfaces']]
    else:
        interfaces = [list(core.SEARCHABLE_CONTENTS[i].
                     __implemented__.interfaces())[0].__identifier__
                      for i in content_types if i in core.SEARCHABLE_CONTENTS]
    #catalog
    dace_catalog = None
    if 'dace' in args:
        dace_catalog = args['dace']
    else:
        dace_catalog = find_catalog('dace')

    #index
    object_provides_index = dace_catalog['object_provides']
    return object_provides_index.any(interfaces)


def states_query(node, **args):
    value = None
    if 'metadata_filter' in args:
        value = args['metadata_filter']

    #catalog
    states = value.get('states', []) if value else []
    dace_catalog = None
    if 'dace' in args:
        dace_catalog = args['dace']
    else:
        dace_catalog = find_catalog('dace')

    #index
    states_index = dace_catalog['object_states']
    if not states:
        return states_index.notany(['archived'])

    if args.get('all_states', False):
        return states_index.all(states)

    return states_index.any(states)


def sources_query(node, **args):
    value = None
    if 'other_filter' in args:
        value = args['other_filter']

    sources = value.get('sources', []) if value else []
    #catalog
    lac_catalog = None
    if 'dace' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    if 'root' in args:
        root = args['root']
    else:
        root = getSite()

    if 'site' in args:
        site = args['site']
    else:
        site = get_site_folder(True)

    default_site = getattr(root, 'default_site', None)
    query = None
    if site and (args.get('force_local_control', False) or site is not default_site):
        object_access = lac_catalog['object_access_control']
        query = object_access.any(['all', str(get_oid(site))])

    if sources:
        value_ids = [str(get_oid(v, v)) for v in sources]
        object_source_site = lac_catalog['object_source_site']
        sources_query = object_source_site.any(value_ids)
        if query:
            query = query & sources_query
        else:
            query = sources_query

    return query


def cities_query(node, **args):
    return None


def countries_query(node, **args):
    value = None
    if 'geographic_filter' in args:
        value = args['geographic_filter']

    if value is None:
        return None

    countries = value.get('country', [])
    if not countries:
        return None

    countries = [countries]
    #catalog
    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    country_index = lac_catalog['object_country']
    countries.append('anywhere')
    return country_index.any([v.lower() for v in countries])


def tree_query(node, **args):
    value = None
    if 'metadata_filter' in args:
        value = args['metadata_filter']

    tree = value.get('tree', {}) if value else {}
    keywords = args.get('keywords', None)
    if (not tree or tree == DEFAULT_TREE) and\
       not keywords:
        return None

    if 'site' in args:
        site = args.get('site')
    else:
        site = get_site_folder(True)

    if keywords:
        keywords = site.get_normalized_keywords(keywords)
        keywords.extend(site.get_normalized_keywords(keywords, 'in'))
        keywords.extend(keywords)
    else:
        normalized_tree = site.get_normalized_tree(tree)
        keywords = get_branches(normalized_tree)
        normalized_tree = site.get_normalized_tree(tree, 'in')
        keywords.extend(get_branches(normalized_tree))

    keywords = set(keywords)
    keywords = [k.lower() for k in keywords]
    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    keywords_index = lac_catalog['object_keywords']
    #query
    return keywords_index.any(keywords)


def text_to_search_query(node, **args):
    value = None
    if 'text_filter' in args:
        value = args['text_filter']

    if value is None:
        return None

    text = value.get('text_to_search', None)
    if text:
        if args.get('defined_search', False):
            text = text.replace('(', '').replace(')', '').lower()
            list_text = [t + '*' for t in re.split(', *', text)]
            text = ' AND '.join(list_text)
        else:
            text += '*'
    else:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    relevant_data_index = lac_catalog['relevant_data']
    query = None
    if text:
        query = relevant_data_index.contains(text)

    return query


def start_end_date_query(node, **args):
    value = None
    if 'temporal_filter' in args:
        value = args['temporal_filter']

    if value is None:
        return None

    start_end_dates = value.get('start_end_dates', None)
    if not start_end_dates:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    start_date = start_end_dates['start_date']
    end_date = start_end_dates['end_date']
    if not start_date and not end_date:
        return None

    if start_date:
        start_date = datetime.datetime.combine(
            start_date,
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))

    if end_date:
        end_date = datetime.datetime.combine(
            end_date,
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))

    start_date_index = lac_catalog['start_date']
    return start_date_index.inrange_with_not_indexed(start_date, end_date)


def created_date_query(node, **args):
    value = None
    if 'temporal_filter' in args:
        value = args['temporal_filter']

    if value is None:
        return None

    created_date = value.get('created_date', None)
    if not created_date:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    created_after = created_date['created_after']
    created_before = created_date['created_before']
    created_at_index = lac_catalog['created_at']
    query = None
    if created_after:
        created_after = datetime.datetime.combine(
            created_after,
            datetime.datetime.min.time()).replace(tzinfo=pytz.UTC)
        query = created_at_index.gt(created_after)

    if created_before:
        created_before = datetime.datetime.combine(
            created_before,
            datetime.datetime.min.time()).replace(tzinfo=pytz.UTC)
        if query is None:
            query = created_at_index.lt(created_before)
        else:
            query = query & created_at_index.lt(created_before)

    return query


def authors_query(node, **args):
    value = None
    if 'contribution_filter' in args:
        value = args['contribution_filter']

    if value is None:
        return None

    authors = value.get('authors', [])
    if not authors:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    authors_index = lac_catalog['object_authors']
    return authors_index.any([get_oid(v) for v in authors])


def artists_query(node, **args):
    value = None
    if 'contribution_filter' in args:
        value = args['contribution_filter']

    if value is None:
        return None

    artists = value.get('artists_ids', [])
    if not artists:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    artists_index = lac_catalog['object_artists']
    return artists_index.any([a.get_id() for a in artists])


def zipcode_query(node, **args):
    value = None
    if 'geographic_filter' in args:
        value = args['geographic_filter']

    if value is None:
        return None

    valid_zipcodes = list(value.get('zipcodes_exp', []))
    if not valid_zipcodes:
        return None

    lac_catalog = None
    if 'lac' in args:
        lac_catalog = args['lac']
    else:
        lac_catalog = find_catalog('lac')

    #index
    object_zipcode = lac_catalog['object_zipcode_txt']
    valid_zipcodes.append('anywhere')
    return object_zipcode.contains(' OR '.join(valid_zipcodes))


def contribution_filter_query(node, **args):
    filter_ = args.get('contribution_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


def geographic_filter_query(node, **args):
    filter_ = args.get('geographic_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


def metadata_filter_query(node, **args):
    filter_ = args.get('metadata_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


def temporal_filter_query(node, **args):
    filter_ = args.get('temporal_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


def text_filter_query(node, **args):
    filter_ = args.get('text_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


def other_filter_query(node, **args):
    filter_ = args.get('other_filter', {})
    if filter_.get('negation', False):
        return Not(get_node_query(node, **args))

    return get_node_query(node, **args)


#********************************************Filter data analyzer


def content_types_analyzer(node, source, validated):
    """Return for example
    {'content_types': {
      'artist': 8610, 'person': 3, 'cinema_review': 769, 'venue': 729,
       'cultural_event': 2487, 'organization': 1, 'review': 4187}
    }
    only includes content type != 0
    """
    if 'metadata_filter' in validated:
        validated['metadata_filter'].pop('content_types', None)

    objects = source(**validated)
    index = find_catalog('system')['content_type']
    intersection = index.family.IF.intersection
    object_ids = getattr(objects, 'ids', objects)
    if isinstance(object_ids, (list, types.GeneratorType)):
        object_ids = index.family.IF.Set(object_ids)

    result = [(content_type, len(intersection(object_ids, oids)))
              for content_type, oids in index._fwd_index.items()]
    result = dict([(k, v) for k, v in result if v != 0])
    return {'content_types': result}


def states_analyzer(node, source, validated):
    """Return for example
    {'states': {
      'editable': 250, 'published': 16264, 'archived': 269, 'active': 3}
    }
    """
    if 'metadata_filter' in validated:
        validated['metadata_filter'].pop('states', None)

    objects = source(**validated)
    index = find_catalog('dace')['object_states']
    intersection = index.family.IF.intersection
    object_ids = getattr(objects, 'ids', objects)
    if isinstance(object_ids, (list, types.GeneratorType)):
        object_ids = index.family.IF.Set(object_ids)

    result = [(state_id, len(intersection(object_ids, oids)))
              for state_id, oids in index._fwd_index.items()]
    result = dict([(k, v) for k, v in result if v != 0])
    return {'states': result}


def authors_analyzer(node, source, validated):
    """Return for example
    {'authors': {
      dict([('7422658066368290778', 1))])
    }
    7422658066368290778 is the oid of the Person object
    """
    validated_value = []
    if 'contribution_filter' in validated:
        validated_value = validated['contribution_filter'].get(
            'authors', validated_value)
        if validated_value:
            validated['contribution_filter'].pop('authors')

    if not validated_value:
        return {'authors': {}}

    objects = source(**validated)

    index = find_catalog('lac')['object_authors']
    intersection = index.family.IF.intersection
    object_ids = getattr(objects, 'ids', objects)
    if isinstance(object_ids, (list, types.GeneratorType)):
        object_ids = index.family.IF.Set(object_ids)

    result = {}
    for author in validated_value:
        author_oid = get_oid(author)
        oids = index._fwd_index.get(author_oid)  # Keyword index with int as key
        if oids:
            count = len(intersection(oids, object_ids))
        else:
            count = 0

        result[str(author_oid)] = count

    return {'authors': result}


def artists_analyzer(node, source, validated):
    """Return for example
    {'artists_ids': {
      dict([('6472212985447771037', 1))])
    }
    6472212985447771037 is the oid of the ArtistInformationSheet object
    """
    validated_value = []
    if 'contribution_filter' in validated:
        validated_value = validated['contribution_filter'].get(
            'artists_ids', validated_value)
        if validated_value:
            validated['contribution_filter'].pop('artists_ids')

    if not validated_value:
        return {'artists_ids': {}}

    objects = source(**validated)
    index = find_catalog('lac')['object_artists']
    intersection = index.family.IF.intersection
    object_ids = getattr(objects, 'ids', objects)
    if isinstance(object_ids, (list, types.GeneratorType)):
        object_ids = index.family.IF.Set(object_ids)

    result = {}
    for artist in validated_value:
        artist_oid = str(get_oid(artist))
        oids = index._fwd_index.get(artist_oid)  # Keyword index with str as key
        if oids:
            count = len(intersection(oids, object_ids))
        else:
            count = 0

        result[artist_oid] = count

    return {'artists_ids': result}


def contribution_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


def geographic_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


def metadata_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


def temporal_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


def text_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


def other_filter_analyzer(node, source, validated):
    return get_analyzed_data(node, source, validated)


#**************************************Filter repr


def default_repr(value, request, template):
    if template:
        return renderers.render(
            template,
            {'value': value},
            request)

    return str(value)


def metadata_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['metadata_filter'].get(template_type, None)
    value_cp = deepcopy(value)
    content_types = value_cp['content_types']
    content_types = [getattr(core.SEARCHABLE_CONTENTS[c], 'type_title', c)
                    for c in content_types if c in core.SEARCHABLE_CONTENTS]
    value_cp['content_types'] = content_types
    tree = value_cp['tree']
    tree = json.dumps(dict(tree))
    value_cp['tree'] = tree
    states = value_cp['states']
    states = [STATES_MEMBER_MAPPING[s] for s in states
             if s in STATES_MEMBER_MAPPING]
    value_cp['states'] = states
    value_cp['title'] = _('Metadata filter')
    return default_repr(value_cp, request, template)


def geographic_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['geographic_filter'].get(template_type, None)
    value_cp = value.copy()
    value_cp['title'] = _('Geographic filter')
    return default_repr(value_cp, request, template)


def temporal_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['temporal_filter'].get(template_type, None)
    value_cp = value.copy()
    value_cp['title'] = _('Temporal filter')
    return default_repr(value_cp, request, template)


def contribution_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['contribution_filter'].get(template_type, None)
    value_cp = value.copy()
    value_cp['title'] = _('Contribution filter')
    return default_repr(value_cp, request, template)


def text_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['text_filter'].get(template_type, None)
    value_cp = value.copy()
    value_cp['title'] = _('Text filter')
    return default_repr(value_cp, request, template)


def other_filter_repr(value, request, template_type='default'):
    template = FILTER_TEMPLATES['other_filter'].get(template_type, None)
    value_cp = value.copy()
    value_cp['title'] = _('Other filter')
    return default_repr(value_cp, request, template)


#****************************************Filter data analyzer


def metadata_filter_data(value):
    result = {}
    metadata_filter = value.get('metadata_filter', {})
    if metadata_filter:
        negation = metadata_filter.get('negation', False)
        content_types = metadata_filter.get('content_types', [])
        result['content_types'] = {
            'is_unique': (len(content_types) == 1) and not negation}

        states = metadata_filter.get('states', [])
        result['states'] = {'is_unique': (len(states) == 1) and not negation}

    return result


def geographic_filter_data(value):
    result = {}
    geographic_filter = value.get('geographic_filter', {})
    if geographic_filter:
        negation = geographic_filter.get('negation', False)
        country = geographic_filter.get('country', None)
        result['country'] = {'is_unique': country is not None and not negation}

        valid_zipcodes = geographic_filter.get('valid_zipcodes', [])
        result['valid_zipcodes'] = {
            'is_unique': (len(valid_zipcodes) == 1) and not negation}

    return result


def temporal_filter_data(value):
    result = {}
    return result


def contribution_filter_data(value):
    result = {}
    contribution_filter = value.get('contribution_filter', {})
    if contribution_filter:
        negation = contribution_filter.get('negation', False)
        authors = contribution_filter.get('authors', [])
        result['authors'] = {'is_unique': (len(authors) == 1) and not negation}

        artists_ids = contribution_filter.get('artists_ids', [])
        result['artists_ids'] = {
            'is_unique': (len(artists_ids) == 1) and not negation}

    return result


def text_filter_data(value):
    result = {}
    text_filter = value.get('text_filter', {})
    if text_filter:
        negation = text_filter.get('negation', False)
        text_to_search = text_filter.get('text_to_search', None)
        result['text_to_search'] = {
            'is_unique': text_to_search not in (None, '') and not negation}

    return result


def other_filter_data(value):
    result = {}
    other_filter = value.get('other_filter', {})
    if other_filter:
        negation = other_filter.get('negation', False)
        sources = other_filter.get('sources', [])
        result['sources'] = {'is_unique': (len(sources) == 1) and not negation}

    return result


#*****************************************Filter Schema


@colander.deferred
def content_types_choices(node, kw):
    request = node.bindings['request']
    localizer = request.localizer
    analyzed_data = node.bindings.get('analyzed_data', {})
    values = []
    registry = get_current_registry()
    if 'content_types' in analyzed_data:
        values = [(c, '{} ({})'.format(
            localizer.translate(
                getattr(registry.content.content_types[c],
                        'type_title', str(c))),
            str(analyzed_data['content_types'].get(c, 0))))
            for c in sorted(analyzed_data['content_types'].keys())]
    else:
        exclude_internal = request.user is None
        values = [(key, getattr(c, 'type_title', c.__class__.__name__))
                  for key, c in list(core.SEARCHABLE_CONTENTS.items())
                  if not exclude_internal or
                  (exclude_internal and not getattr(c, 'internal_type', False))]

    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(values=values, multiple=True)


@colander.deferred
def states_choices(node, kw):
    request = node.bindings['request']
    localizer = request.localizer
    analyzed_data = node.bindings.get('analyzed_data', {})
    values = []
    if 'states' in analyzed_data:
        values = [(state, '{} ({})'.format(
            localizer.translate(STATES_MEMBER_MAPPING[state]),
            str(analyzed_data['states'].get(state, 0))))
            for state in sorted(analyzed_data['states'].keys())]
    else:
        values = [(k, STATES_MEMBER_MAPPING[k])
                  for k in sorted(STATES_MEMBER_MAPPING.keys())]

    return Select2Widget(values=values, multiple=True)


@colander.deferred
def sources_choices(node, kw):
    request = node.bindings['request']
    values = [(get_oid(s), s.title) for s in
              getattr(request.root, 'site_folders', [])
              if s.title != 'default']
    values = sorted(values, key=lambda e: e[1])
    values.insert(0, ('self', _('This site')))
    return Select2Widget(values=values, multiple=True)


@colander.deferred
def cities_choices(node, kw):
    """Zip Codes must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities_ides'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="address-entry",
        create=False,
        multiple=True)


@colander.deferred
def countries_choices(node, kw):
    """Zip Codes must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_countries_ides'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="address-entry",
        create=False,
        add_clear=True)


@colander.deferred
def authors_choices(node, kw):
    """Country must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    analyzed_data = node.bindings.get('analyzed_data', {})
    authors_data = analyzed_data.get('authors', {})
    values = []

    def title_getter(oid):
        author = None
        try:
            author = get_obj(int(oid))
        except Exception:
            return oid

        title = getattr(author, 'title', author.__name__)
        if authors_data:
            title += ' ('+str(authors_data.get(oid, 0))+')'

        return title

    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_user'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        multiple=True,
        title_getter=title_getter)


@colander.deferred
def artists_choices(node, kw):
    """Country must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    analyzed_data = node.bindings.get('analyzed_data', {})
    authors_data = analyzed_data.get('artists_ids', {})
    values = []
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_artists'})

    def title_getter(oid):
        try:
            obj = get_obj(int(oid), None)
            if obj:
                title = obj.title
                if authors_data:
                    title += ' ('+str(authors_data.get(oid, 0))+')'

                return title
            else:
                return oid
        except Exception as e:
            log.warning(e)
            return oid

    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        multiple=True,
        title_getter=title_getter
        )


@colander.deferred
def keyword_widget(node, kw):
    request = node.bindings['request']
    can_create = 100
    levels = request.get_site_folder.get_tree_nodes_by_level()
    return KeywordsTreeWidget(
        min_len=1,
        max_len=DEFAULT_TREE_LEN,
        can_create=can_create,
        levels=levels)


@colander.deferred
def zipcodes_widget(node, kw):
    """Zip Codes must be in the select tag for the initialization"""
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_cities'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="address-entry",
        create=True,
        multiple=True)


class ZipcodeFilterSchema(Schema):
    """Schema for ZipcodeFilterSchema"""

    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    country = colander.SchemaNode(
        colander.String(),
        widget=countries_choices,
        title=_('Country'),
        description=_("You can enter the name of the country associated to contents to be displayed."),
        missing='',
        query=countries_query,
        )

    city = colander.SchemaNode(
        colander.Set(),
        widget=cities_choices,
        title=_('Cities'),
        description=_("You can enter the names of the cities associated to contents to be displayed."),
        default=[],
        missing=[],
        query=cities_query,
        )

    zipcode = colander.SchemaNode(
        colander.Set(),
        widget=zipcodes_widget,
        title=_('Zipcodes'),
        missing=[],
        description=_('You can enter zipcodes of cities associated to contents to be displayed.'),
        query=zipcode_query
        )

    def deserialize(self, cstruct=colander.null):
        self.get('zipcode').missing = []
        self.get('city').missing = []
        self.get('country').missing = ''
        appstruct = super(ZipcodeFilterSchema, self).deserialize(cstruct)
        country = appstruct.get('country', None)
        if not appstruct['zipcode']:
            appstruct['valid_zipcodes'] = []
            appstruct['zipcodes_exp'] = []
        else:
            valid_zipcodes = [z for z in appstruct['zipcode']
                              if z.find('*') == -1]
            zipcodes = [z.replace('*', '.')+'*' for z in appstruct['zipcode']
                        if z not in valid_zipcodes]
            result = get_zipcodes(zipcodes, country)
            valid_zipcodes.extend([str(item) for c in result
                                   for item in c['fields']['zipcode']
                                   if match_in(str(item), zipcodes)])
            valid_zipcodes.extend([z.split(" ")[0] for z in valid_zipcodes])
            appstruct['valid_zipcodes'] = list(set(valid_zipcodes))
            appstruct['zipcodes_exp'] = [z.replace('*', '?') for z in appstruct['zipcode']]

        if appstruct.get('city', []):
            valid_zipcodes = get_zipcodes_from_cities(
                appstruct['city'], country)
            valid_zipcodes.extend([z.split(" ")[0] for z in valid_zipcodes])
            valid_zipcodes = list(set(valid_zipcodes))
            to_validate = [z for z in valid_zipcodes
                           if z not in appstruct['valid_zipcodes']]
            appstruct['valid_zipcodes'].extend(to_validate)
            appstruct['zipcodes_exp'].extend(to_validate)

        return appstruct


class MetadataFilter(Schema):
    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    content_types = colander.SchemaNode(
        colander.Set(),
        widget=content_types_choices,
        title=_('Types'),
        description=_('You can select the content types to be displayed.'),
        default=[],
        missing=[],
        query=content_types_query,
        analyzer=content_types_analyzer
        )

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        widget=keyword_widget,
        title=_('Categories'),
        description=_('You can select the categories of the contents to be displayed.'),
        default=DEFAULT_TREE,
        missing=None,
        query=tree_query
    )

    states = colander.SchemaNode(
        colander.Set(),
        widget=states_choices,
        title=_('States'),
        description=_('You can select the states of the contents to be displayed.'),
        default=[],
        missing=[],
        query=states_query,
        analyzer=states_analyzer
    )


class StartEndDates(Schema):

    start_date = colander.SchemaNode(
        colander.Date(),
        title=_('Start date'),
        missing=None,
        )

    end_date = colander.SchemaNode(
        colander.Date(),
        title=_('End date'),
        missing=None,
        description_bottom=True,
        description=_('You can select the start and end dates of the cultural events to be displayed.')
        )


class CreatedDates(Schema):

    created_after = colander.SchemaNode(
        colander.Date(),
        title=_('Created after'),
        missing=None
        )

    created_before = colander.SchemaNode(
        colander.Date(),
        title=_('Created before'),
        description_bottom=True,
        description=_('You can select the creation dates of contents to be displayed.'),
        missing=None,
        )


class TemporalSchema(Schema):

    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    start_end_dates = omit(StartEndDates(
        widget=SimpleMappingWidget(css_class="filter-block"
                                             " object-well"
                                             " default-well"),
        query=start_end_date_query
        ),
            ["_csrf_token_"])

    created_date = omit(CreatedDates(
        widget=SimpleMappingWidget(css_class="filter-block"
                                             " object-well"
                                             " default-well"),
        query=created_date_query
        ),
            ["_csrf_token_"])


class ContributionFilterSchema(Schema):

    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    authors = colander.SchemaNode(
        colander.Set(),
        widget=authors_choices,
        title=_('Authors'),
        description=_('You can enter the authors names of the contents to be displayed.'),
        default=[],
        missing=[],
        query=authors_query,
        analyzer=authors_analyzer
        )

    artists_ids = colander.SchemaNode(
        colander.Set(),
        widget=artists_choices,
        title=_('Artists'),
        description=_('You can enter the artists names to display the associated contents.'),
        default=[],
        missing=[],
        query=artists_query,
        analyzer=artists_analyzer
        )


class TextFilterSchema(Schema):
    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    text_to_search = colander.SchemaNode(
        colander.String(),
        title=_('Text'),
        description=_("You can enter the words that appear in the contents to be displayed."),
        default='',
        missing='',
        query=text_to_search_query
    )


class OtherFilterSchema(Schema):
    negation = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Check the box to exclude values entered below.'),
        )

    sources = colander.SchemaNode(
        colander.Set(),
        widget=sources_choices,
        title=_('Sources'),
        description=_("You can select the sites to which the contents to be displayed belong."),
        default=[],
        missing=[],
        query=sources_query
    )

    def deserialize(self, cstruct=colander.null):
        self.get('sources').missing = []
        appstruct = super(OtherFilterSchema, self).deserialize(cstruct)
        request = get_current_request()
        if getattr(request, 'view_name', None) != 'addsitefolder' and \
           'sources' in appstruct:
            if 'self' in appstruct['sources']:
                site = get_site_folder(True, request)
                if site:
                    sources = list(appstruct['sources'])
                    sources.remove('self')
                    sources.append(str(get_oid(site)))
                    appstruct['sources'] = list(set(sources))

        return appstruct


class FilterSchema(Schema):

    metadata_filter = omit(MetadataFilter(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-cog",
            activator_title=_('Metadata filter')),
        query=metadata_filter_query,
        analyzer=metadata_filter_analyzer,
        repr_value=metadata_filter_repr,
        filter_analyzer=metadata_filter_data
        ),
            ["_csrf_token_"])

    geographic_filter = omit(ZipcodeFilterSchema(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-map-marker",
            activator_title=_('Geographic filter')),
        query=geographic_filter_query,
        analyzer=geographic_filter_analyzer,
        repr_value=geographic_filter_repr,
        filter_analyzer=geographic_filter_data
        ),
            ["_csrf_token_"])

    temporal_filter = omit(TemporalSchema(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-calendar",
            activator_title=_('Temporal filter')),
        query=temporal_filter_query,
        analyzer=temporal_filter_analyzer,
        repr_value=temporal_filter_repr,
        filter_analyzer=temporal_filter_data
        ),
            ["_csrf_token_"])

    contribution_filter = omit(ContributionFilterSchema(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-user",
            activator_title=_('Contribution filter')),
        query=contribution_filter_query,
        analyzer=contribution_filter_analyzer,
        repr_value=contribution_filter_repr,
        filter_analyzer=contribution_filter_data
        ),
            ["_csrf_token_"])

    text_filter = omit(TextFilterSchema(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-pencil",
            activator_title=_('Text filter')),
        query=text_filter_query,
        analyzer=text_filter_analyzer,
        repr_value=text_filter_repr,
        filter_analyzer=text_filter_data
        ),
            ["_csrf_token_"])

    other_filter = omit(OtherFilterSchema(
        widget=SimpleMappingtWidget(
            mapping_css_class='controled-form',
            ajax=True,
            activator_css_class="glyphicon glyphicon-option-horizontal",
            activator_title=_('Other filter')),
        query=other_filter_query,
        analyzer=other_filter_analyzer,
        repr_value=other_filter_repr,
        filter_analyzer=other_filter_data
        ),
            ["_csrf_token_"])


@view_config(
    name='filter',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class FilterView(FormView):
    title = _('Filter')
    name = 'filter'
    coordinates = 'main'
    schema = FilterSchema()
    formid = 'formfilter'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'
    filter_template = 'lac:views/templates/filter.pt'

    def __init__(self,
                 context,
                 request,
                 parent=None,
                 wizard=None,
                 stepid=None,
                 **kwargs):
        super(FilterView, self).__init__(context,
                                         request,
                                         parent,
                                         wizard,
                                         stepid,
                                         **kwargs)
        self.error = False
        self.validated = {}
        self._validated = {}
        if self.params('filter_result') is not None or \
           kwargs.get('filter_result', None) is not None:
            self.calculate_posted_filter()

        self.schema = select(FilterSchema(),
                             ['metadata_filter', 'geographic_filter',
                              'temporal_filter', 'contribution_filter',
                              'text_filter', 'other_filter'])

    def calculate_posted_filter(self):
        form, reqts = self._build_form()
        form.formid = self.viewid + '_' + form.formid
        posted_formid = None
        values = self.request.POST or self.request.GET
        if '__formid__' in values:
            posted_formid = values['__formid__']

        if posted_formid is not None and posted_formid == form.formid:
            try:
                controls = values.items()
                validated = form.validate(controls)
                self.validated = validated
                self.validated['request'] = self.request
                self._validated = deepcopy(validated)
            except Exception as e:
                log.warning(e)

    def bind(self):
        analyzed_data = getattr(self, 'analyzed_data', {})
        appstruct = getattr(self, '_validated', {})
        error = getattr(self, 'error', False)
        return {'analyzed_data': analyzed_data,
                'appstruct': appstruct,
                'error': error}

    def default_data(self):
        return getattr(self, '_validated', {})

    def omit_filters(self, filters):
        self.schema = omit(self.schema, filters)

    def select_filters(self, filters):
        self.schema = select(self.schema, filters)

    def analyze_data(self, source):
        self.analyzed_data = get_analyzed_data(
            self.schema, source, getattr(self, 'validated', {}))

    def get_body(self, filter_data):
        filter_body = self.content(
            args=filter_data,
            template=self.filter_template)['body']
        return filter_body


def get_filter(view, url, omit=(),
               select=(), source=None):
    filter_instance = FilterView(view.context, view.request)
    view.filter_instance = filter_instance
    if omit:
        filter_instance.omit_filters(omit)

    if select:
        filter_instance.select_filters(select)

    if source:
        filter_instance.analyze_data(source)

    filter_form = filter_instance.update()
    filter_body = filter_form['coordinates']\
                             [filter_instance.coordinates][0]['body']
    filter_data = {'filter_body': filter_body,
                   'filter_url': url,
                   'filter_source': view.name,
                   'filter_message': view.title,
                   'filter_resul': view.params('filter_result') is not None,
                   'filter_validated': filter_instance.validated}
    return filter_form, filter_data


def repr_filter(filter_data, request, template_type='default'):
    filter_schema = FilterSchema()
    global_template = FILTER_TEMPLATES['global'][template_type]
    filter_template = FILTER_TEMPLATES['filter'][template_type]
    all_filters = []
    for filter_ in filter_data:
        filter_values = []
        for child in filter_schema.children:
            name = child.name
            value = filter_.get(name, _marker)
            if hasattr(child, 'repr_value') and \
               value is not _marker:
                filter_values.append(
                    child.repr_value(
                        value, request, template_type))

        values = {'bodies': filter_values}
        all_filters.append(renderers.render(
            filter_template,
            values, request))

    values = {'bodies': all_filters}
    body = renderers.render(
        global_template,
        values, request)
    return body


class AnyOids(Any):

    def _apply(self, names):
        # self._value is the list of oids
        if isinstance(self._value, (list, types.GeneratorType)):
            oids = self.index.family.IF.Set(self._value)
        return oids


def find_entities(user=None,
                  add_query=None,
                  intersect=None,
                  include_site=False,
                  force_site=False,
                  site=None,
                  force_publication_date=False,
                  sort_on=None,
                  reverse=False,
                  limit=None,
                  filters=[],
                  filter_op='and',
                  **args):
    """intersect is a list or LFSet of oids.
    Parameter force_publication_date can be None, False or True.
    True forces the date to today, False force it to today only if the user
    has not the PortalManager role. None disable the index completely.
    """
    if intersect is not None and len(intersect) == 0:
        return ResultSet([], 0, None)

    request = args['request'] if 'request' in args\
        else get_current_request()
    site = site if site else get_site_folder(True, request)
    hold_filter = getattr(site, 'hold_filter', True) if request.user else True
    schema = FilterSchema()
    site_query = None
    if force_site or (include_site and hold_filter):
        site_filters = deepcopy(getattr(site, 'filters', []))
        #get the site query
        if site_filters:
            site_query = get_filters_query(schema, site_filters, 'or')

    dace_catalog = find_catalog('dace')
    lac_catalog = find_catalog('lac')
    system_catalog = find_catalog('system')
    filters = deepcopy(filters)
    root = getSite()
    for filter_ in filters:
        filter_['dace'] = dace_catalog
        filter_['lac'] = lac_catalog
        filter_['system'] = system_catalog
        filter_['root'] = root
        filter_['site'] = site

    query = get_filters_query(schema, filters, filter_op)
    if site_query:
        query = and_op(site_query, query)

    if add_query:
        query = and_op(query, add_query)

    if args:
        args['dace'] = dace_catalog
        args['lac'] = lac_catalog
        args['system'] = system_catalog
        args['root'] = root
        args['site'] = site
        args_query = get_filters_query(schema, [args], filter_op)
        query = and_op(query, args_query)

    if user:
        root = getSite()
        site_id = str(get_oid(site))
        access_keys = lac_catalog['access_keys']
        keys = getattr(user, '__access_keys__', {}).get(site_id, _marker)
        if keys is _marker:
            keys = core.generate_access_keys(user, root, site)

        keys = list(keys)
        keys.append('always')
        query = and_op(query, access_keys.any(keys))

    #add publication interval
    if force_publication_date is not None and (
            force_publication_date or \
            not has_any_roles(
                roles=(('PortalManager', site), 'PortalManager'))):
        start_date = end_date = datetime.datetime.now()
        start_date = datetime.datetime.combine(
            start_date,
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))
        end_date = datetime.datetime.combine(
            end_date,
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))
        start_date_index = lac_catalog['publication_start_date']
        query = and_op(query, start_date_index.inrange_with_not_indexed(
            start_date, end_date))

    #    print(query.print_tree())
    #    from timeit import default_timer as timer
    #    start = timer()
    if intersect is not None:
        query = AnyOids(dace_catalog['oid'], intersect) & query

    try:
        result_set = query.execute()
    except ParseError as error:
        log.warning(error)
        return ResultSet([], 0, None)
    #    end = timer() - start
    #    print(end)

    if sort_on is not None:
        result_set = result_set.sort(
            lac_catalog[sort_on], reverse=reverse, limit=limit)

    return result_set


def find_more_contents(obj, state=[]):
    user = get_current()
    request = get_current_request()
    registry = request.registry
    content_type = registry.content.typeof(obj)
    query, args = obj.get_more_contents_criteria()
    if args is None:
        return []

    if 'objects' in args:
        return args['objects']

    if content_type:
        args['request'] = request
        return find_entities(
            user=user,
            metadata_filter={'content_types': [content_type],
                             'states': state},
            add_query=query,
            include_site=True,
            sort_on='release_date',
            reverse=True,
            **args)

    return []


def get_entities_by_title(interfaces, title, **args):
    user = get_current()
    lac_catalog = find_catalog('lac')
    #index
    title_index = lac_catalog['object_title']
    #query
    titles = []
    if isinstance(title, (list, tuple, set)):
        titles = [normalize_title(t) for t in title]
    else:
        titles = [normalize_title(title)]

    query = title_index.any(titles)
    return find_entities(
        user=user,
        interfaces=interfaces,
        add_query=query,
        include_site=True,
        **args)


def visible_in_site(site, obj, **args):
    filter_ = obj.get_visibility_filter()
    filter_.update(args)
    results = find_entities(
        intersect=[get_oid(obj)],
        force_site=True,
        site=site, **filter_)
    return len(results) >= 1


def get_alerts_by_subject(oids=[], subject=None):
    if not oids and not subject:
        return []

    lac_catalog = find_catalog('lac')
    favorites_index = lac_catalog['related_contents']
    if not oids:
        oid = get_oid(subject, None)
        if oid is None:
            return []

        oids = [oid]

    query = favorites_index.any(oids)
    return find_entities(
        interfaces=[IAlert],
        add_query=query)
