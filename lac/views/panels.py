# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import json
from pyramid import renderers
from pyramid_layout.panel import panel_config
from pyramid.threadlocal import get_current_registry

from substanced.util import get_oid

from pontus.util import update_resources
from dace.objectofcollaboration.entity import Entity
from dace.util import getSite, getAllBusinessAction, get_obj, getBusinessAction
from dace.objectofcollaboration.principal.util import get_current
from daceui.interfaces import IDaceUIAPI

from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac.content.resources import arango_server, create_collection
from lac.content.processes.cultural_event_management.\
    behaviors import CreateCulturalEvent
from lac.content.processes.lac_view_manager.\
    behaviors import SeeGames
from lac import _
from lac.core import (
    SearchableEntity, can_access, site_widget_config,
    IMPORT_SOURCES)
from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity
    )
from lac.content.smart_folder import SmartFolder
from lac.views.filter import find_entities, find_more_contents
from lac.content.interface import IBaseReview, ISmartFolder, get_subinterfaces
from lac.views.lac_view_manager.search import (
    SearchView)
from lac.views import GeoSearchForm
from lac.utilities.utils import (
    get_actions_navbar,
    footer_navbar_body,
    get_site_folder,
    deepcopy,
    update_actions)
from lac.fr_lexicon import normalize_title
from lac.contextual_help_messages import CONTEXTUAL_HELP_MESSAGES
from lac.views.lac_view_manager.\
    questionnaire import (
        CURRENT_QUEST)


#SHORTNER_URL = 'http://localhost:5000/'
SHORTNER_URL = 'https://ssl.lac.com/urlshortener/'

LEVEL_MENU = 3

MORE_NB = 20

DEFAULT_FOLDER_COLORS = {'usual_color': 'white, #2d6ca2',
                         'hover_color': 'white, #2d6ca2'}

GROUPS_PICTO = {
    'Add': (0, 'glyphicon glyphicon-plus'),
    'See': (1, 'glyphicon glyphicon-eye-open'),
    'Edit': (2, 'glyphicon glyphicon-pencil'),
    'Directory': (3, 'glyphicon glyphicon-book'),
    'More': (4, 'glyphicon glyphicon-cog'),
}


def site_validator(self):
    site = get_site_folder(True, self.request)
    return self.widget_name in getattr(site, 'widgets', [])


@panel_config(
    name='usermenu',
    context=Entity,
    renderer='templates/panels/usermenu.pt'
    )
class Usermenu_panel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        user = get_current(self.request)
        resources = deepcopy(getattr(
            self.request, 'resources', {'js_links': [], 'css_links': []}))
        search_view_instance = SearchView(self.context, self.request)
        search_view_result = search_view_instance()
        search_body = ''
        result = {'css_links': [], 'js_links': []}
        if isinstance(search_view_result, dict) and \
           'coordinates' in search_view_result:
            search_body = search_view_result['coordinates'][search_view_instance.coordinates][0]['body']
            result['css_links'] = [c for c in search_view_result['css_links']
                                   if c not in resources['css_links']]
            result['js_links'] = [c for c in search_view_result['js_links']
                                  if c not in resources['js_links']]

        result['search_body'] = search_body
        result['view'] = self
        result['alerts'] = []
        if hasattr(user, 'get_alerts'):
            site = get_site_folder(True, self.request)
            result['alerts'] = user.get_alerts(site=site)

        result['login_action'] = None
        if self.request.user is None:
            root = self.request.root
            actions = getBusinessAction(
                context=root, request=self.request,
                process_id='usermanagement', node_id='login')
            if actions:
                actions_result = update_actions(root, self.request, actions)
                #actions_result = (action_updated, action_alert_messages,
                #                  action_resources, action_informations)
                if actions_result[3]:
                    result['login_action'] = actions_result[3][0]

        update_resources(self.request, result)
        return result


@panel_config(
    name='lac_contents',
    context=CreationCulturelleApplication,
    renderer='templates/panels/lac_contents.pt'
    )
class CreationCulturelleContents(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.view_name != '':
            return {'condition': False}

        result = {}
        result['condition'] = True
        return result


@panel_config(
    name='lac_footer',
    renderer='templates/panels/lac_footer.pt'
    )
class CreationCulturelleFooter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        root = getSite()

        def actions_getter():
            return [a for a in root.actions
                    if getattr(a.action, 'style', '') == 'button']

        actions_navbar = get_actions_navbar(
            actions_getter, self.request, ['footer-action'])
        return {'navbar_body': footer_navbar_body(
            self, self.context, actions_navbar)}


@panel_config(
    name='navigation_bar',
    context=Entity,
    renderer='templates/panels/navigation_bar.pt'
    )
class NavigationBar(object):

    template_sub_menu = 'templates/panels/sub_menu.pt'

    def __init__(self, context, request):
        site = get_site_folder(True)
        site_id = get_oid(site)
        self.context = context
        self.request = request
        self.default_folder = SmartFolder(title=_('My private folders'),
                                          style=DEFAULT_FOLDER_COLORS,
                                          )
        self.default_folder.folder_order[site_id] = 1000

    def get_sub_menu(self, nodes, parent_name, current_level, active_folder, site_id):
        body = renderers.render(self.template_sub_menu,
                                {'nodes': nodes,
                                 'active_folder': active_folder,
                                 'parent_name': parent_name,
                                 'view': self,
                                 'current_level': current_level,
                                 'maxi_level': LEVEL_MENU,
                                 'site_id': site_id
                                },
                                self.request)
        return body

    def get_folder_parent(self, node):
        if node.parents:
            return node.parents[0]

        return self.default_folder

    def get_folder_children(self, node, site_id):
        user = get_current()
        children = node.children if node is not self.default_folder\
            else self.default_folder.volatile_children
        nodes = [sf for sf in children if can_access(user, sf)]
        nodes = sorted(nodes, key=lambda e: e.get_order(site_id))
        return nodes

    def get_folder_id(self, node):
        return get_oid(node)

    def get_folder_name(self, node):
        if node is self.default_folder:
            return 'default_folder'

        return normalize_title(node.name).replace(' ', '-')

    def __call__(self):
        site = get_site_folder(True)
        site_id = get_oid(site)
        nodes = find_entities(
            interfaces=[ISmartFolder],
            metadata_filter={'states': ['published']},
            force_local_control=True)
        active_folder_id = None
        active_folder = None
        if self.request.GET:
            active_folder_id = dict(self.request.GET._items).get('folderid', None)

        try:
            if active_folder_id:
                active_folder = get_obj(int(active_folder_id))
        except (TypeError, ValueError):
            active_folder = None

        if self.request.user:
            my_folders = getattr(get_current(), 'folders', [])
            my_folders = [folder for folder in my_folders
                          if isinstance(folder, SmartFolder) and
                          'private' in folder.state and
                          not folder.parents]
            if my_folders:
                self.default_folder.volatile_children = my_folders

        nodes = [sf for sf in nodes if not sf.parents]
        if getattr(self.default_folder, 'volatile_children', []):
            nodes.append(self.default_folder)

        nodes = sorted(nodes, key=lambda e: e.get_order(site_id))
        return {'nodes': nodes,
                'active_folder': active_folder,
                'view': self,
                'current_level': 1,
                'maxi_level': LEVEL_MENU,
                'site_id': site_id}


@site_widget_config(
    name='carousel_widget',
    title=_('Carousel widget'),
    validator=site_validator,
    renderer='lac:views/templates/site_widgets/carousel_widget.pt')
@panel_config(
    name='carousel',
    context=CreationCulturelleApplication,
    renderer='templates/panels/carousel_captions.pt'
    )
class CarouselCaptions(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.view_name not in ('', 'index', '@@index'):
            return {'items': []}

        reviews = find_entities(
            interfaces=get_subinterfaces(IBaseReview),
            metadata_filter={'states': ['published']},
            sort_on='release_date',
            reverse=True,
            include_site=True)
        result = []
        for review in reviews:
            if review.picture and getattr(review, 'showcase_review', False):
                result.append(review)

            if len(result) >= 5:
                break

        return {'items': result}


@site_widget_config(
    name='calendar_widget',
    title=_('Calendar widget'),
    validator=site_validator,
    renderer='lac:views/templates/site_widgets/calendar_widget.pt')
@panel_config(
    name='calendar',
    context=Entity,
    renderer='templates/panels/calendar.pt'
    )
class Calendar(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        root = getSite()
        url = self.request.resource_url(root, 'creationculturelapi')
        return {'url': url}


@panel_config(
    name='lateral_menu',
    context=Entity,
    renderer='templates/panels/lateral_menu.pt'
    )
class LateralMenu(object):
    actions = {
        CreateCulturalEvent: ('culturaleventmanagement', 'creat', 'btn-warning'),
        SeeGames: ('lacviewmanager', 'seegames', 'btn-primary')}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        root = getSite()
        actions = []
        for action_class, data in self.actions.items():
            item_actions = getAllBusinessAction(
                root,
                self.request,
                process_id=data[0],
                node_id=data[1])
            action = None
            if item_actions:
                action = item_actions[0]

            actions.append({'title': action_class.title,
                            'action': action,
                            'unavailable_link': getattr(
                                action_class, 'unavailable_link', None),
                            'order': getattr(action_class, 'style_order', 100),
                            'style_btn': data[2],
                            'style_picto': getattr(action_class,
                                                   'style_picto', '')})

        actions = sorted(actions, key=lambda e: e['order'])
        return {'items': actions}


def group_actions(actions):
    groups = {}
    for action in actions:
        group_id = _('More')
        if action[1].node_definition.groups:
            group_id = action[1].node_definition.groups[0]

        group = groups.get(group_id, None)
        if group:
            group.append(action)
        else:
            groups[group_id] = [action]

    for group_id, group in groups.items():
        groups[group_id] = sorted(
            group, key=lambda e: getattr(e[1], 'style_order', 0))
    groups = sorted(list(groups.items()),
                    key=lambda g: GROUPS_PICTO.get(g[0], ("default", 0))[0])
    return groups


@panel_config(
    name='adminnavbar',
    context=Entity,
    renderer='templates/panels/admin_navbar.pt'
    )
class Adminnavbar_panel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        root = getSite()
        if not global_user_processsecurity(None, root):
            return {'error': True}

        dace_ui_api = get_current_registry().getUtility(IDaceUIAPI,
                                                        'dace_ui_api')
        actions = dace_ui_api.get_actions([root], self.request)
        admin_actions = [a for a in actions
                         if getattr(a[1], 'style_descriminator', '') ==
                         'admin-action']
        return {'groups': group_actions(admin_actions),
                'pictos': {g: v[1] for g, v in GROUPS_PICTO.items()},
                'error': False}


@panel_config(
    name='social_share',
    context=Entity,
    renderer='templates/panels/social_share.pt'
    )
class SocialShare(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.request.view_name != 'index' or \
           not isinstance(self.context, SearchableEntity) or \
           not self.context.is_published:
            return {'condition': False}

        return {'request': self.request,
                'object': self.context,
                'condition': True,
                'shortner_url': SHORTNER_URL}


@panel_config(
    name='social_share_toggle',
    context=Entity,
    renderer='templates/panels/social_share_toggle.pt'
    )
class SocialToggleShare(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {'object': self.context,
                'shortner_url': SHORTNER_URL}


@site_widget_config(
    name='more_contents_widget',
    title=_('More contents widget'),
    validator=site_validator,
    renderer='lac:views/templates/site_widgets/more_contents_widget.pt')
@panel_config(
    name='more_contents',
    context=SearchableEntity,
    renderer='templates/panels/more_contents.pt'
    )
@panel_config(
    name='more_contents',
    context=CreationCulturelleApplication,
    renderer='templates/panels/more_contents.pt'
    )
class MoreContents(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        is_root = False
        if self.request.view_name in ('', 'index', '@@index'):
            objects = getattr(self.context, 'connections_to', [])
            objects.extend(getattr(self.context, 'connections_from', []))
            more_result = []
            more = []
            root = getSite()
            if self.context is root:
                date = datetime.datetime.now()
                start_end_dates = {'start_date': date,
                                   'end_date': date}
                more_result = find_entities(
                    metadata_filter={'content_types': ['cultural_event'],
                                     'states': ['published']},
                    temporal_filter={'start_end_dates': start_end_dates},
                    sort_on='modified_at', reverse=True,
                    include_site=True)
                is_root = True
            else:
                more_result = find_more_contents(
                                    self.context,
                                    state=['published', 'active'])

            for index, obj in enumerate(more_result):
                more.append(obj)
                if index > MORE_NB:
                    break

            if self.context in more:
                more.remove(self.context)

            objects.extend(more)
            objects = sorted(list(set(objects)),
                key=lambda e: getattr(e, 'release_date', e.modified_at),
                reverse=True)
        else:
            objects = []

        return {'contents': objects,
                'is_root': is_root,
                'request': self.request}


@panel_config(
    name='contextual_help',
    context=Entity,
    renderer='templates/panels/contextual_help.pt'
    )
class ContextualHelp(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if not self.request.cookies.get('contextual_help', True):
            return {'condition': False}

        user = get_current()
        messages = [CONTEXTUAL_HELP_MESSAGES.get((self.context.__class__,
                                                  s, self.request.view_name),
                                                 None)
                    for s in self.context.state]
        messages.append(CONTEXTUAL_HELP_MESSAGES.get(
                        (self.context.__class__, 'any', self.request.view_name),
                        None))
        messages = [m for m in messages if m is not None]
        messages = [item for sublist in messages for item in sublist]
        messages = sorted(messages, key=lambda m: m[2])
        messages = [renderers.render(
            m[1], {'context': self.context, 'user': user}, self.request)
            for m in messages if m[0] is None or m[0](self.context, user)]
        return {'messages': messages,
                'condition': True}


@panel_config(
    name='promotions_panel',
    context=SearchableEntity,
    renderer='templates/panels/promotions_panel.pt'
    )
class PromotionsPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        promotions = getattr(self.context, 'promotions', [])
        return {'promotions': promotions}


@panel_config(
    name='cookies_panel',
    context=Entity,
    renderer='templates/panels/cookies.pt'
    )
class CookiesPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if not self.request.cookies.get('accept_cookies', False):
            return {'accept': False}

        return {'accept': True}


@site_widget_config(
    name='map_widget',
    title=_('Map widget'),
    validator=site_validator,
    renderer='lac:views/templates/site_widgets/map_widget.pt')
@panel_config(
    name='map_panel',
    context=CreationCulturelleApplication,
    renderer='templates/panels/map.pt'
    )
class MapPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        root = getSite()
        options = {}
        options['locations'] = {}
        options['show_all'] = True
        resources = deepcopy(getattr(
            self.request, 'resources', {'js_links': [], 'css_links': []}))
        search_view_instance = GeoSearchForm(self.context, self.request)
        search_view_result = search_view_instance()
        search_body = ''
        result = {'css_links': [], 'js_links': []}
        if isinstance(search_view_result, dict) and \
           'coordinates' in search_view_result:
            search_body = search_view_result['coordinates'][search_view_instance.coordinates][0]['body']
            result['css_links'] = [c for c in search_view_result['css_links']
                                   if c not in resources['css_links']]
            result['js_links'] = [c for c in search_view_result['js_links']
                                  if c not in resources['js_links']]

        result['search_body'] = search_body
        result['options'] = json.dumps(options)
        result['url'] = self.request.resource_url(
            root, '@@creationculturelapi',
            query={'op': 'find_geo_cultural_event'})

        update_resources(self.request, result)
        return result


@site_widget_config(
    name='map_widget',
    title=_('Map widget'),
    validator=site_validator,
    renderer='lac:views/templates/site_widgets/map_widget.pt')
@panel_config(
    name='map_activator',
    context=CreationCulturelleApplication,
    renderer='templates/panels/map_activator.pt'
    )
class MapActivatorPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {}


@panel_config(
    name='labels',
    context=Entity,
    renderer='templates/panels/labels.pt'
    )
class LabelsPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        labels = getattr(self.context, 'labels', [])
        labels_data = [{'title': l.title,
                        'img': l.picture.url} for l in labels]
        labels_data = sorted(labels_data, key=lambda e: e['title'])
        site = self.request.get_site_folder
        site_oid = get_oid(site)
        if site_oid != self.context.source_site:
            orig_site = get_obj(self.context.source_site)
            if orig_site.favicon:
                labels_data.append({'title': orig_site.title,
                                    'img': orig_site.favicon.url,
                                    'url': orig_site.urls_ids[0]})

        source_id = getattr(self.context, 'source_data', {}).get(
            'source_id', None)
        source_data = IMPORT_SOURCES.get(source_id, None)
        if source_data:
            labels_data.append({'title': source_data['title'],
                                'img': self.request.static_url(source_data['icon']),
                                'url': source_data['url']})

        return {'labels': labels_data}


@panel_config(
    name='questionnaire_panel',
    context=Entity,
    renderer='templates/panels/questionnaire_panel.pt'
    )
class Questionnaire_panel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        site = get_site_folder(True, self.request)
        if self.request.view_name in ('@@resetpassword', '@@registration',
                                      'login', '@@login') or \
           not getattr(site, 'activate_questionnaire', False):
            return {'questionnaire': None}

        user = get_current()
        email = getattr(user, 'email', '')
        if email:
            db = arango_server.db("lac")
            collection = create_collection(db, CURRENT_QUEST)
            doc = collection.get_first_example({"email": email})
            if doc:
                return {'questionnaire': None}

        resources = deepcopy(getattr(
            self.request, 'resources', {'js_links': [], 'css_links': []}))
        result = {'css_links': [], 'js_links': []}
        root = self.request.root
        actions = getBusinessAction(
            context=root, request=self.request,
            process_id='lacviewmanager', node_id='questionnaire')
        result['questionnaire'] = None
        result['current_questionnaire'] = CURRENT_QUEST
        if actions:
            actions_result = update_actions(root, self.request, actions)
            #actions_result = (action_updated, action_alert_messages,
            #                  action_resources, action_informations)
            if actions_result[3]:
                result['questionnaire'] = actions_result[3][0]
                result['css_links'] = [c for c in actions_result[2].get('css_links', [])
                                       if c not in resources['css_links']]
                result['js_links'] = [c for c in actions_result[2].get('js_links', [])
                                      if c not in resources['js_links']]

        update_resources(self.request, result)
        return result


@panel_config(
    name='improve_panel',
    context=Entity,
    renderer='templates/panels/improve_panel.pt'
    )
class Improve_panel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        site = get_site_folder(True, self.request)
        if not getattr(site, 'activate_improve', False):
            return {'improve': None}

        resources = deepcopy(getattr(
            self.request, 'resources', {'js_links': [], 'css_links': []}))
        result = {'css_links': [], 'js_links': []}
        root = self.request.root
        actions = getBusinessAction(
            context=root, request=self.request,
            process_id='lacviewmanager', node_id='improve')
        result['improve'] = None

        if actions:
            actions_result = update_actions(root, self.request, actions)
            #actions_result = (action_updated, action_alert_messages,
            #                  action_resources, action_informations)
            if actions_result[3]:
                result['improve'] = actions_result[3][0]
                result['css_links'] = [c for c in actions_result[2].get('css_links', [])
                                       if c not in resources['css_links']]
                result['js_links'] = [c for c in actions_result[2].get('js_links', [])
                                      if c not in resources['js_links']]

        update_resources(self.request, result)
        return result


@panel_config(
    name='analytics_panel',
    context=Entity,
    renderer='templates/panels/analytics_panel.pt'
    )
class AnalyticsPanel(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        user = self.request.user
        userid = get_oid(self.request.user) if user else 'anonymous'
        is_contributor = 'true' if user and \
            getattr(user, '_contents_value', []) else (user and 'false' or 'anonymous')
        return {'userid': userid,
                'is_contributor': is_contributor}
