# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
import datetime
from pyramid.view import view_config

from substanced.util import Batch

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from dace.util import getSite
from pontus.view import BasicView
from pontus.widget import Select2Widget
from pontus.schema import Schema, select

from lac.content.processes.lac_view_manager.behaviors import (
    Search)
from lac import _
from .widget import SearchTextInputWidget, SearchFormWidget
from lac.content.processes import get_states_mapping
from lac.content.keyword import ROOT_TREE
from lac import core
from lac.views.filter import (
    FilterView, find_entities, FilterSchema,
    artists_choices, cities_choices,
    DEFAULT_TREE)
from lac.utilities.cinema_utility import next_weekday
from lac.utilities.utils import get_month_range, deepcopy


CONTENTS_MESSAGES = {
    '0': _(u"""No element found"""),
    '1': _(u"""One element found"""),
    '*': _(u"""${nember} elements found""")
    }


def _whatever_dates():
    return {
        'start_date': None,
        'end_date': None
    }


def _today_dates():
    today = datetime.datetime.today()
    return {
        'start_date': today,
        'end_date': today
    }


def _tomorrow_dates():
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    return {
        'start_date': tomorrow,
        'end_date': tomorrow
    }


def _week_end_dates():
    today = datetime.datetime.today()
    start_weekend = next_weekday(today, 5)
    end_weekend = next_weekday(today, 6)
    return {
        'start_date': start_weekend,
        'end_date': end_weekend
    }


def _week_dates():
    today = datetime.datetime.today()
    end_weekend = next_weekday(today, 6)
    return {
        'start_date': today,
        'end_date': end_weekend
    }


def _next_week_dates():
    today = datetime.datetime.today()
    start_weekend = next_weekday(today, 0, 1)
    end_weekend = next_weekday(today, 6, 1)
    return {
        'start_date': start_weekend,
        'end_date': end_weekend
    }


def _Within_15_dates():
    start_weekend = datetime.datetime.today()
    end_weekend = start_weekend + datetime.timedelta(days=15)
    return {
        'start_date': start_weekend,
        'end_date': end_weekend
    }


def _one_month_dates():
    today = datetime.datetime.today()
    _, end_date = get_month_range(today)
    return {
        'start_date': today,
        'end_date': end_date
    }


def _next_month_dates():
    st_date, end_date = get_month_range(
        datetime.datetime.today(),
        next_month=True)
    return {
        'start_date': st_date,
        'end_date': end_date
    }


DEFAULT_DATES = {
    0: (_('Whatever'), _whatever_dates),
    1: (_('Today'), _today_dates),
    2: (_('Tomorrow'), _tomorrow_dates),
    3: (_('This week-end'), _week_end_dates),
    4: (_('This week'), _week_dates),
    5: (_('Next week'), _next_week_dates),
    6: (_('Within 15 days'), _Within_15_dates),
    7: (_('Within one month'), _one_month_dates),
    8: (_('Next month'), _next_month_dates)
}


@colander.deferred
def thematic_widget(node, kw):
    request = node.bindings['request']
    values = request.get_site_folder.get_keywords_by_level()
    if len(values) >= 1:
        values = [(k, k) for k in sorted(values[1])]

    return Select2Widget(values=values, multiple=True)


@colander.deferred
def dates_widget(node, kw):
    values = [(k, v[0]) for k, v in
              sorted(DEFAULT_DATES.items(), key=lambda e: e[0])]
    return Select2Widget(values=values)


class CalendarSearchSchema(FilterSchema):

    thematics = colander.SchemaNode(
        colander.Set(),
        widget=thematic_widget,
        title=_('Thematics'),
        description=_('You can select the thematics of the cultural events to be displayed.'),
        default=[],
        missing=[]
    )

    city = colander.SchemaNode(
        colander.Set(),
        widget=cities_choices,
        title=_('Where ?'),
        default=[],
        missing=[],
        description=_("You can enter the names of the cities where cultural events to be displayed take place.")
        )

    dates = colander.SchemaNode(
        colander.Int(),
        widget=dates_widget,
        title=_('When ?'),
        missing=1,
        description=_('You can select the dates of the cultural events to be displayed.'),
        default=1
        )

    artists_ids = colander.SchemaNode(
        colander.Set(),
        widget=artists_choices,
        title=_('Artists'),
        description=_('You can enter the artists names to display the associated contents.'),
        default=[],
        missing=[]
        )

    text_to_search = colander.SchemaNode(
        colander.String(),
        description=_("You can enter the words that appear in the cultural events to be displayed."),
        title=_('keywords'),
        default='',
        missing=''
    )

    def deserialize(self, cstruct=colander.null):
        appstruct = super(CalendarSearchSchema, self).deserialize(cstruct)
        thematics = appstruct.get('thematics', [])
        dates = appstruct.get('dates', 0)
        appstruct = {
            'metadata_filter': {
                'content_types': {'cultural_event'},
                'states': ['published'],
                'tree': deepcopy(DEFAULT_TREE)
                },
            'text_filter': {
                'text_to_search': appstruct.pop('text_to_search', '')
                },
            'contribution_filter': {
                'artists_ids': appstruct.pop('artists_ids', [])
                },
            'geographic_filter': {
                'city': appstruct.pop('city', [])
                },
            'temporal_filter': {
                'start_end_dates': DEFAULT_DATES[dates][1]()
                }
        }
        for thematic in thematics:
            appstruct['metadata_filter']['tree'][ROOT_TREE][thematic] = {}

        return appstruct


@view_config(
    name='advanced_search',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AdvancedSearchView(FilterView):
    title = _('Advanced search')
    name = 'advanced_search'
    behaviors = [Search]
    formid = 'formadvanced_search'
    wrapper_template = 'pontus:templates/views_templates/view_wrapper.pt'

    def before_update(self):
        if not self.request.user:
            self.schema = select(CalendarSearchSchema(),
                                 ['thematics', 'city',
                                  'dates',
                                  'artists_ids',
                                  'text_to_search'])

        return super(AdvancedSearchView, self).before_update()

    def update(self):
        self.calculate_posted_filter()
        if self.validated:
            result_view = SearchResultView(self.context, self.request)
            result_view.validated = self.validated
            result = result_view.update()
            return result
        else:
            return super(AdvancedSearchView, self).update()


@view_config(
    name='search_result',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SearchResultView(BasicView):
    title = ''
    name = 'search_result'
    validators = [Search.get_validator()]
    template = 'lac:views/lac_view_manager/templates/search_result.pt'
    viewid = 'search_result'

    def update(self):
        self.execute(None)
        user = get_current()
        validated = getattr(self, 'validated', {})
        posted = self.request.POST or self.request.GET or {}
        posted = posted.copy()
        clear_posted = False
        if not validated:
            if posted:
                clear_posted = True
                searcinstance = SearchView(self.context, self.request,
                                           filter_result=True)
                if searcinstance.validated:
                    validated = searcinstance.validated

        objects = find_entities(
            user=user,
            sort_on='release_date', reverse=True,
            include_site=True,
            **validated)
        url = self.request.resource_url(
            self.context, self.request.view_name, query=posted)
        batch = Batch(objects, self.request,
                      default_size=core.BATCH_DEFAULT_SIZE,
                      url=url)
        #clear posted values: See usermenu panel
        if clear_posted:
            if self.request.POST:
                self.request.POST.clear()
            elif self.request.GET:
                self.request.GET.clear()

        batch.target = "#results_contents"
        len_result = batch.seqlen
        index = str(len_result)
        if len_result > 1:
            index = '*'

        self.title = _(CONTENTS_MESSAGES[index],
                       mapping={'nember': len_result})
        result_body = []
        for obj in batch:
            render_dict = {'object': obj,
                           'current_user': user,
                           'state': get_states_mapping(user, obj,
                                   getattr(obj, 'state_or_none', [None])[0])}
            body = self.content(args=render_dict,
                                template=obj.templates['default'])['body']
            result_body.append(body)

        result = {}
        values = {'bodies': result_body,
                  'batch': batch}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result

    def before_update(self):
        super(SearchResultView, self).before_update()
        self.title = _('${lac_title} contents',
              mapping={'lac_title': self.request.root.title})


@colander.deferred
def text_to_search_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_entities'})
    advanced_search_url = request.resource_url(
        root, '@@advanced_search')
    return SearchTextInputWidget(
        url=ajax_url,
        advanced_search_url=advanced_search_url,
        placeholder=_('Ex. théâtre le 13 juillet'))


class SearchSchema(Schema):
    widget = SearchFormWidget()

    text_to_search = colander.SchemaNode(
        colander.String(),
        widget=text_to_search_widget,
        title='',
        default='',
        missing='',
        )

    def deserialize(self, cstruct=colander.null):
        appstruct = super(SearchSchema, self).deserialize(cstruct)
        appstruct = {
            'text_filter':
            {'text_to_search': appstruct.pop('text_to_search', '')},
        }
        return appstruct


@view_config(
    name='simple_search',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SearchView(FilterView):
    title = _('Search')
    name = 'search'
    schema = select(SearchSchema(), ['text_to_search'])
    behaviors = [Search]
    formid = 'formsearch'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'

    def before_update(self):
        self.schema = select(SearchSchema(), ['text_to_search'])
        root = getSite()
        self.action = self.request.resource_url(
            root, '@@search_result')


DEFAULTMAPPING_ACTIONS_VIEWS.update({Search: AdvancedSearchView})
