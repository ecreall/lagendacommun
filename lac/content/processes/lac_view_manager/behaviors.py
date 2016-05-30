# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import pytz
import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid import renderers
from pyramid.threadlocal import get_current_request

from substanced.util import get_oid

import html_diff_wrapper
from dace.util import getSite
from dace.interfaces import IEntity
from dace.objectofcollaboration.principal.util import (
    has_role, get_current, has_any_roles)
from dace.processinstance.core import PROCESS_HISTORY_KEY
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from lac.content.interface import (
    ICreationCulturelleApplication, IGame, IParticipativeEntity)
from ..user_management.behaviors import global_user_processsecurity
from lac.core import access_action, can_access
from lac import _
from lac.utilities.utils import get_site_folder, to_localized_time
from lac.views.filter import find_entities
from lac.utilities.alerts_utility import alert


class Search(InfiniteCardinality):
    isSequential = False
    context = IEntity

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(
            request.resource_url(root, '@@search_result'))


def home_processsecurity_validation(process, context):
    return True


@access_action()
class SeeHome(InfiniteCardinality):
    isSequential = False
    context = ICreationCulturelleApplication
    actionType = ActionType.automatic
    processsecurity_validation = home_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}


def seemy_roles_validation(process, context):
    return has_role(role=('Member',))


def seemyc_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class SeeMyContents(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-th-list'
    style_order = 4
    isSequential = False
    context = ICreationCulturelleApplication
    roles_validation = seemy_roles_validation
    processsecurity_validation = seemyc_processsecurity_validation

    def contents_nb(self):
        user = get_current()
        return len([o for o in getattr(user, 'contents', [])])

    def start(self, context, request, appstruct, **kw):
        return {}


def seecontents_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Moderator', site))


def seecontents_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class SeeContentsToModerate(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'lac-icon icon-stack'
    style_order = 5
    isSequential = False
    context = ICreationCulturelleApplication
    roles_validation = seecontents_roles_validation
    processsecurity_validation = seecontents_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}


def contact_processsecurity_validation(process, context):
    site = get_site_folder(True)
    for contact in getattr(site, 'contacts', []):
        if contact.get('email', None):
            return True

    return False


class Contact(InfiniteCardinality):
    style = 'button'
    style_descriminator = 'footer-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-send'
    submission_title = _('Send')
    style_order = 1
    isSequential = False
    context = IEntity
    #processsecurity_validation = contact_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        subject = appstruct.get('subject')
        mail = appstruct.get('message')
        sender = appstruct.get('email')
        services = appstruct.get('services')
        alert('email', [sender], list(services),
              {'subject': subject, 'body': mail})
        appstruct.pop('_csrf_token_')
        user = request.user
        appstruct['user'] = 'Anonymous'
        if user:
            appstruct['user'] = get_oid(user)

        now = datetime.datetime.now(tz=pytz.timezone('Europe/Paris'))
        appstruct['date'] = now.isoformat()
        appstruct['services'] = str(appstruct['services'])
        site = get_site_folder(True, request)
        appstruct['site'] = get_oid(site)
        alert('arango', [], ["lac.contact"], appstruct)
        #alert slack
        appstruct['date'] = to_localized_time(
            now, translate=True)
        text = 'Sujet: {subject}\n Message: {message}\n User: {user}\n Nom: {name}\n Email: {email}\n Date: {date}\n\n Service: {services}'.format(**appstruct)
        alert('slack', [], ['lac_contact'], {'text': text})
        if user and not getattr(user, 'email', ''):
            user.email = sender

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(
            request.resource_url(context, ''))


def games_processsecurity_validation(process, context):
    request = get_current_request()
    cached_value = getattr(
        request, 'cache_games_processsecurity_validation', None)
    if cached_value is not None:
        return cached_value

    site = str(get_oid(get_site_folder(True)))
    games = find_entities(
        interfaces=[IGame],
        metadata_filter={'states': ['published']},
        other_filter={'sources': [site]},
        force_publication_date=True)
    cached_value = bool(games)
    request.cache_games_processsecurity_validation = cached_value
    return cached_value


class SeeGames(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'octicon octicon-gift'
    title = _('Games & Competitions')
    style_order = 2
    isSequential = False
    context = ICreationCulturelleApplication
    processsecurity_validation = games_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}


def history_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('PortalManager', site), ('Owner', context)))


def history_processsecurity_validation(process, context):
    return getattr(context, 'annotations', {}).get(PROCESS_HISTORY_KEY, {}) and \
           global_user_processsecurity(process, context)


class SeeEntityHistory(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'footer-entity-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-time'
    title = _('History')
    style_order = 2
    isSequential = False
    context = IEntity
    processsecurity_validation = history_processsecurity_validation
    roles_validation = history_roles_validation

    def start(self, context, request, appstruct, **kw):
        return {}


def cont_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('PortalManager', site), ('Owner', context)))


def cont_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class SeeContributors(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'footer-entity-action'
    style_interaction = 'modal-action'
    style_picto = 'md md-group'
    title = _('Contributors')
    style_order = 2
    isSequential = False
    context = IParticipativeEntity
    processsecurity_validation = cont_processsecurity_validation
    roles_validation = cont_roles_validation

    def start(self, context, request, appstruct, **kw):
        return {}


class DiffView(InfiniteCardinality):
    title = _('Differences')
    isSequential = False
    context = ICreationCulturelleApplication
    processsecurity_validation = seecontents_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        source = appstruct['source']
        targets = appstruct['targets']
        if can_access(user, source) and all(can_access(user, target)
                                            for target in targets):
            diff_bodies = {}
            source_view = renderers.render(
                source.templates.get('diff', None),
                {'object': source},
                request)

            for target in targets:
                target_view = renderers.render(
                    target.templates.get('diff', None),
                    {'object': target},
                    request)
                soupt, textdiff = html_diff_wrapper.render_html_diff(
                    source_view, target_view)
                diff_bodies[target] = (textdiff, get_oid(target))

            return {'context_view': source_view,
                    'contents': diff_bodies}

        return {}

    def redirect(self, context, request, **kw):
        return kw


def seealldup_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Moderator', site), ('SiteAdmin', site),
                                'Admin'))


class SeeAllDuplicates(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-duplicate'
    style_order = 100
    isSequential = False
    context = ICreationCulturelleApplication
    roles_validation = seealldup_roles_validation
    processsecurity_validation = seecontents_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}


def seealerts_roles_validation(process, context):
    return has_role(role=('Member',))


def seealerts_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class SeeAlerts(InfiniteCardinality):
    isSequential = False
    context = ICreationCulturelleApplication
    processsecurity_validation = seealerts_processsecurity_validation
    roles_validation = seealerts_roles_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        site = get_site_folder(True, request)
        if hasattr(user, 'get_alerts'):
            for alert in user.get_alerts(site=site):
                alert.unsubscribe(user)

        return {}


class Questionnaire(InfiniteCardinality):
    style_descriminator = 'questionnaire-action'
    submission_title = _('Save')
    isSequential = False
    context = ICreationCulturelleApplication

    def start(self, context, request, appstruct, **kw):
        appstruct.pop('_csrf_token_')
        user = request.user
        appstruct['user'] = 'Anonymous'
        if user:
            appstruct['user'] = get_oid(user)

        now = datetime.datetime.now(tz=pytz.timezone('Europe/Paris'))
        appstruct['date'] = now.isoformat()
        site = get_site_folder(True, request)
        appstruct['site'] = get_oid(site)
        alert('arango', [], ["lac."+appstruct['id']], appstruct)
        #alert slack
        appstruct['date'] = to_localized_time(
            now, translate=True)
        text = 'Aimez-vous la nouvelle version: {new_version}\n '
        if appstruct['new_version'] == 'False':
            text += 'Pourquoi non: {explanation}\n '

        text += 'Aimeriez-vous une application mobile: {mobile_application}\n \n User: {user}\n Email: {email}\n Date: {date}'
        text = text.format(**appstruct)
        alert('slack', [], ['questionnaire'], {'text': text})
        if user and not getattr(user, 'email', ''):
            user.email = appstruct.get('email', '')

        return {}

    def redirect(self, context, request, **kw):
        referrer = request.path_url
        came_from = request.session.setdefault(
            'lac.came_from', referrer)
        return HTTPFound(location=came_from)


class Improve(InfiniteCardinality):
    style_descriminator = 'improve-action'
    submission_title = _('Save')
    isSequential = False
    context = ICreationCulturelleApplication

    def start(self, context, request, appstruct, **kw):
        appstruct.pop('_csrf_token_')
        site = get_site_folder(True, request)
        contacts = [c for c in getattr(site, 'contacts', [])
                    if c.get('email', None)]
        if contacts:
            subject = "Avis d'un utilisateur"
            mail = appstruct.get('improvement')
            sender = appstruct.get('email')
            alert('email', [sender], [contacts[-1].get('email')],
                  {'subject': subject, 'body': mail})

        user = request.user
        appstruct['user'] = 'Anonymous'
        if user:
            appstruct['user'] = get_oid(user)

        now = datetime.datetime.now(tz=pytz.timezone('Europe/Paris'))
        appstruct['date'] = now.isoformat()
        appstruct['site'] = get_oid(site)
        alert('arango', [], ["lac."+appstruct['id']], appstruct)
        #alert slack
        appstruct['date'] = to_localized_time(
            now, translate=True)
        text = '{improvement}\n User: {user}\n URL: {url}\n Email: {email}\n Date: {date}'.format(**appstruct)
        alert('slack', [], ['improve'], {'text': text})
        if user and not getattr(user, 'email', ''):
            user.email = appstruct.get('email', '')

        return {}

    def redirect(self, context, request, **kw):
        referrer = request.path_url
        came_from = request.session.setdefault(
            'lac.came_from', referrer)
        return HTTPFound(location=came_from)

#TODO behaviors
