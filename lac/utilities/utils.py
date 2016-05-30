# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Sophie Jazwiecki

import math
import calendar
import datetime
import collections
import pytz
import string
import random
from babel.core import Locale
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from bs4 import BeautifulSoup
from pyramid import renderers
from pyramid.threadlocal import get_current_request

from substanced.util import itertools, merge_url_qs, Batch as BatchBase

from dace.processinstance.activity import ActionType
from dace.objectofcollaboration.principal.util import get_current
from daceui.interfaces import IDaceUIAPI
from deform_treepy.utilities.tree_utility import tree_to_keywords

from lac.content.processes import get_states_mapping
from lac import _, log
from .ical_date_utility import getDatesFromString, set_recurrence

try:
    _LETTERS = string.letters
except AttributeError: #pragma NO COVER
    _LETTERS = string.ascii_letters


DATE_FORMAT = {
    'defined_literal': {
        'day_month_year': _('On ${month} ${day} ${year}'),
        'day_month': _('On ${month} ${day}'),
        'day': _('On ${day}'),
        'day_hour_minute_month_year': _("On ${month} ${day} ${year} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_minute_month': _("On ${month} ${day} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_minute': _("On ${day} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_month_year': _("On ${month} ${day} ${year} at ${hour} o'clock"),
        'day_hour_month': _("On ${month} ${day} at ${hour} o'clock"),
        'day_hour': _("On ${day} at ${hour} o'clock")
    },
    'direct_literal': {
        'day_month_year': _('${month} ${day} ${year}'),
        'day_month': _('${month} ${day}'),
        'day': _('${day}'),
        'day_hour_minute_month_year': _("${month} ${day} ${year} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_minute_month': _("${month} ${day} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_minute': _("${day} at ${hour} o'clock and ${minute} minutes"),
        'day_hour_month_year': _("${month} ${day} ${year} at ${hour} o'clock"),
        'day_hour_month': _("${month} ${day} at ${hour} o'clock"),
        'day_hour': _("${day} at ${hour} o'clock")
    },
    'digital': {
        'day_month_year': _('${month}/${day}/${year}'),
        'day_month': _('${month}/${day}'),
        'day': _('${day}'),
        'day_hour_minute_month_year': _('${month}/${day}/${year} ${hour}:${minute}'),
        'day_hour_minute_month': _('${month}/${day} ${hour}:${minute}'),
        'day_hour_minute': _('${day} ${hour}:${minute}'),
        'day_hour_month_year': _('${month}/${day}/${year} ${hour}:00'),
        'day_hour_month': _('${month}/${day} ${hour}:00'),
        'day_hour_month': _('${day} ${hour}:00')
    }
}


def gen_random_token():
    length = random.choice(range(10, 16))
    chars = _LETTERS + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def to_localized_time(
    date, request=None, date_from=None,
    date_only=False, format_id='digital',
    ignore_month=False, ignore_year=False,
    add_day_name=False, translate=False):
    if request is None:
        request = get_current_request()

    if date_from is None:
        date_from = datetime.datetime.now()

    hour = getattr(date, 'hour', None)
    minute = getattr(date, 'minute', None)
    date_dict = {
        'year': date.year,
        'day': date.day,
        'month': date.month,
        'hour': hour if not date_only else None,
        'minute': minute if not date_only and minute != 0 else None
    }
    if ignore_month:
        month = ((date_from.month != date_dict['month'] or \
                  date_from.year != date_dict['year']) and \
                 date_dict['month']) or None
        date_dict['month'] = month
        if month is None:
            date_dict['year'] = None

    if ignore_year and date_dict['year']:
        year = ((date_from.year != date_dict['year']) and \
                date_dict['year']) or None
        date_dict['year'] = year

    date_dict = {key: value for key, value in date_dict.items() if value}
    if 'minute' in date_dict and date_dict['minute'] < 10:
        date_dict['minute'] = '0' + str(date_dict['minute'])

    localizer = request.localizer
    if format_id.endswith('literal'):
        locale = Locale(localizer.locale_name)
        if 'day' in date_dict:
            if date_dict['day'] == 1:
                date_dict['day'] = localizer.translate(_('1st'))

            if add_day_name:
                weekday = date.weekday()
                day_name = locale.days['format']['wide'][weekday]
                date_dict['day'] = localizer.translate(
                    _('${name} ${day}',
                      mapping={'name': day_name, 'day': date_dict['day']}))

        if 'month' in date_dict:
            date_dict['month'] = locale.months['format']['wide'][date_dict['month']]

    date_format_id = '_'.join(sorted(list(date_dict.keys())))
    format = DATE_FORMAT[format_id].get(date_format_id)
    if translate:
        return localizer.translate(_(format, mapping=date_dict))

    return _(format, mapping=date_dict)


def get_month_range(start_date=None, next_month=False):
    if start_date is None:
        start_date = datetime.date.today()

    month = start_date.month
    year = start_date.year
    if next_month:
        month = 1 if start_date.month == 12 else start_date.month + 1
        if month == 1:
            year += 1

    start_date = start_date.replace(day=1, month=month, year=year)
    _, days_in_month = calendar.monthrange(year, month)
    end_date = start_date + datetime.timedelta(days=days_in_month-1)
    return (start_date, end_date)


def get_site_folder(force=False, request=None):
    if request is None:
        request = get_current_request()

    if force:
        return getattr(request, 'get_site_folder', None)

    return getattr(request, 'site_folder', None)


def get_valid_moderation_service():
    return get_site_folder(True).get_all_services(
        kinds=['moderation'],
        user=get_current(),
        delegation=False)


def deepcopy(obj):
    result = None
    if isinstance(obj, (dict, PersistentDict)):
        result = {}
        for key, value in obj.items():
            result[key] = deepcopy(value)

    elif isinstance(obj, (list, tuple, set, PersistentList)):
        result = [deepcopy(value) for value in obj]
    else:
        result = obj

    return result


def flatten(l):
    for element in l:
        if isinstance(element, collections.Iterable) and \
           not isinstance(element, str):
            for sub in flatten(element):
                yield sub
        else:
            yield element


def synchronize_tree():
    """Return a property. The getter of the property returns the
    ``_tree`` attribute of the instance on which it's defined. The setter
    of the property calls ``synchronize_tree()``.

      class SomeContentType(Persistent):
          tree = synchronize_tree()
    """
    def _get(self):
        return getattr(self, '_tree', None)

    def _set(self, newtree):
        self._tree = PersistentDict(deepcopy(newtree))
        self.keywords = PersistentList([k.lower() for
                                        k in tree_to_keywords(self._tree)])
    return property(_get, _set)


def dates(propertyname):
    """Return a dates property.
    """
    def _get(self):
        return getattr(self, propertyname + '_dates_str', '')

    def _set(self, dates_str):
        """Set _dates_str, start_date, end_date and recurrence attributes
        """
        setattr(self, propertyname + '_dates_str', dates_str)
        dates = getDatesFromString(self, dates_str)
        # Set start and end dates from dates (list of list representing datetime)
        if not dates:
            setattr(self, propertyname + '_start_date', None)
            setattr(self, propertyname + '_end_date', None)
            setattr(self, propertyname + '_recurrence', '')
            return

        now = datetime.datetime.now(tz=pytz.UTC)
        if dates[0]:
            setattr(self, propertyname + '_start_date',
                    datetime.datetime(
                        dates[0][0], dates[0][1],
                        dates[0][2], tzinfo=pytz.UTC))
            setattr(self, propertyname + '_end_date',
                    datetime.datetime(
                        dates[0][0], dates[0][1],
                        dates[0][2], 23, 59, 59, tzinfo=pytz.UTC))
        else:
            setattr(self, propertyname + '_start_date', now)
            setattr(self, propertyname + '_end_date',
                    datetime.datetime(
                        now.year, now.month,
                        now.day, 23, 59, 59, tzinfo=pytz.UTC))

        setattr(self, propertyname + '_recurrence',
                set_recurrence(dates, dates_str))

    return property(_get, _set)


def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    element = soup.body
    if element is None:
        return ''

    text = ' '.join(element.stripped_strings)
    return text


def html_article_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    articles = soup.find_all('div', 'article-body')
    if articles:
        article = articles[0]
        
        text = ' '.join(article.stripped_strings)
        return text

    return ''


def get_modal_actions(actions_call, request):
    dace_ui_api = request.registry.getUtility(
        IDaceUIAPI, 'dace_ui_api')
    actions = [(a.context, a.action) for a in actions_call]
    action_updated, messages, \
    resources, actions = dace_ui_api.update_actions(
        request, actions)
    return action_updated, messages, resources, actions


def update_actions(context, request, actions):
    dace_ui_api = request.registry.getUtility(
        IDaceUIAPI, 'dace_ui_api')
    actions = [(context, a) for a in actions]
    action_updated, messages, \
    resources, actions = dace_ui_api.update_actions(
        request, actions)
    return action_updated, messages, resources, actions


def get_actions_navbar(actions_getter, request, descriminators):
    result = {}
    actions = []
    isactive = True
    update_nb = 0
    while isactive and update_nb < 2:
        actions = actions_getter()
        modal_actions = [a for a in actions
                         if getattr(a.action, 'style_interaction', '') ==
                         'modal-action']
        isactive, messages, \
        resources, modal_actions = get_modal_actions(modal_actions, request)
        update_nb += 1

    modal_actions = [(a['action'], a) for a in modal_actions]
    result['modal-action'] = {'isactive': isactive,
                              'messages': messages,
                              'resources': resources,
                              'actions': modal_actions
                              }
    for descriminator in descriminators:
        descriminator_actions = [a for a in actions
                                 if getattr(a.action,
                                            'style_descriminator', '') ==
                                 descriminator]
        descriminator_actions = sorted(
            descriminator_actions,
            key=lambda e: getattr(e.action, 'style_order', 0))
        result[descriminator] = descriminator_actions

    return result


def default_navbar_body(view, context, actions_navbar):
    global_actions = actions_navbar['global-action']
    text_actions = actions_navbar['text-action']
    modal_actions = actions_navbar['modal-action']['actions']
    template = 'lac:views/templates/navbar_actions.pt'
    result = {
        'global_actions': global_actions,
        'modal_actions': dict(modal_actions),
        'text_actions': text_actions,
    }
    return renderers.render(template, result, view.request)


def footer_navbar_body(view, context, actions_navbar):
    global_actions = actions_navbar['footer-action']
    modal_actions = actions_navbar['modal-action']['actions']
    template = 'lac:views/templates/footer_navbar_actions.pt'
    result = {
        'footer_actions': global_actions,
        'modal_actions': dict(modal_actions)
    }
    return renderers.render(template, result, view.request)


navbar_body_getter = default_navbar_body


def services_block_body(view, context, actions_navbar):
    actions = actions_navbar['service-action']
    modal_actions = actions_navbar['modal-action']['actions']
    template = 'lac:views/templates/service_actions.pt'
    user = get_current()
    services = []
    if hasattr(context, 'get_services'):
        services = context.get_services(user=user)

    result_servicesbody = []
    for obj in services:
        expired = obj.is_expired()
        object_values = {'object': obj,
                         'expired': expired,
                         'state': get_states_mapping(user, obj,
                               getattr(obj, 'state_or_none', [None])[0])}
        body = view.content(args=object_values,
                            template=obj.templates['default'])['body']
        result_servicesbody.append(body)

    result = {
        'actions': actions,
        'modal_actions': dict(modal_actions),
        'row_len': math.ceil(len(actions)/4),
        'row_len_services': math.ceil(len(services)/4),
        'services': result_servicesbody
    }
    return renderers.render(template, result, view.request)


def footer_block_body(view, context, actions_navbar):
    footer_actions = actions_navbar['footer-entity-action']
    modal_actions = actions_navbar['modal-action']['actions']
    template = 'lac:views/templates/footer_entity_actions.pt'
    result = {
        'footer_actions': footer_actions,
        'modal_actions': dict(modal_actions)
    }
    return renderers.render(template, result, view.request)


class ObjectRemovedException(Exception):
    pass


def generate_navbars(view, context, request):
    def actions_getter():
        return [a for a in context.actions
                if a.action.actionType != ActionType.automatic]

    all_actions = get_actions_navbar(
        actions_getter, request,
        ['service-action', 'footer-entity-action', 'global-action',
         'text-action', 'admin-action', 'body-action'])
    all_actions['global-action'].extend(
        all_actions.pop('admin-action'))
    if getattr(context, '__parent__', None) is None:
        raise ObjectRemovedException("Object removed")

    actions_bodies = []
    for action in all_actions['body-action']:
        object_values = {'action': action}
        body = view.content(args=object_values,
                            template=action.action.template)['body']
        actions_bodies.append(body)

    isactive = all_actions['modal-action']['isactive']
    messages = all_actions['modal-action']['messages']
    resources = all_actions['modal-action']['resources']
    return {'isactive': isactive,
            'messages': messages,
            'resources': resources,
            'navbar_body': navbar_body_getter(view, context, all_actions),
            'services_body': services_block_body(view, context, all_actions),
            'footer_body': footer_block_body(view, context, all_actions),
            'body_actions': actions_bodies}


def generate_body_sub_actions(view, context, request):
    def actions_getter():
        return [a for a in context.actions
                if a.action.actionType != ActionType.automatic]

    actions_body = get_actions_navbar(
        actions_getter, request, ['body-sub-action'])
    if getattr(context, '__parent__', None) is None:
        raise ObjectRemovedException("Object removed")

    actions_bodies = []
    for action in actions_body['body-sub-action']:
        object_values = {'action': action}
        body = view.content(args=object_values,
                            template=action.action.template)['body']
        actions_bodies.append(body)

    return {'body_actions': actions_bodies}


class ConditionalBatch(BatchBase):
    def __init__(self, condition, seq, request, url=None, default_size=10, toggle_size=40,
                 seqlen=None):
        if url is None:
            url = request.url

        try:
            num = int(request.params.get('batch_num', 0))
        except (TypeError, ValueError):
            num = 0
        if num < 0:
            num = 0

        try:
            size = int(request.params.get('batch_size', default_size))
        except (TypeError, ValueError):
            size = default_size
        if size < 1:
            size = default_size

        if seqlen is None:
            # won't work if seq is a generator
            seqlen = len(seq)

        start = num
        items = itertools.islice(seq, start, seqlen)
        last_index = start
        valid_items = []
        index = 0
        for item in items:
            if condition(item):
                valid_items.append(item)

            last_index = index
            index += 1
            valid_len = len(valid_items)
            log.info(str(index)+"/"+str(seqlen)+": "+getattr(item, 'title', ''))
            log.info(str(valid_len)+"*********************"+str(size))
            if valid_len == size:
                break

        last_index = last_index + start
        length = len(valid_items)
        items = valid_items
        last = int(math.ceil(seqlen / float(size)) - 1)

        first_url = None
        prev_url = None
        next_url = None
        toggle_url = None

        if num:
            first_url = merge_url_qs(url, batch_size=size, batch_num=0)
        if start >= size:
            prev_url = merge_url_qs(
                url, batch_size=size, batch_num=num-last_index)
        if seqlen >= last_index:
            next_url = merge_url_qs(
                url, batch_size=size, batch_num=last_index+1)

        if prev_url or next_url:
            toggle_url = merge_url_qs(
                url,
                batch_size=toggle_size,
                batch_num=0,
                multicolumn=False,
                )

        self.startitem = start
        self.enditem = last_index - 1
        self.last = last
        self.seqlen = seqlen
        self.items = items
        self.num = num
        self.size = size
        self.length = length
        self.required = bool(prev_url or next_url)
        self.multicolumn = False
        self.toggle_url = toggle_url
        self.toggle_text = 'Single column'
        self.first_url = first_url
        self.prev_url = prev_url
        self.next_url = next_url
        self.last_url = None
