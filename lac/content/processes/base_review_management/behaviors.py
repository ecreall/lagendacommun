# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_role,
    has_any_roles,
    grant_roles,
    get_current)
from dace.processinstance.core import ActivityExecuted
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)
from pontus.file import OBJECT_DATA

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    IBaseReview,
    IReview,
    ICinemaReview,
    IInterview)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.\
    cultural_event_management.behaviors import (
        update_orders, remove_empty_orders,
        extract_artists, submit_artists)
from lac.views.filter import visible_in_site
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)
from lac.content.processes.artist_management.behaviors import (
    publish_artist)


def submit_review(context):
    #TODO submit and duplicate the review
    pass


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles((('Owner', obj),
                                  'SiteAdmin', 'Moderator'))
        return result


def seereview_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                ('Moderator', site)))


@access_action(access_key=get_access_key)
class SeeReview(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = IReview
    actionType = ActionType.automatic
    processsecurity_validation = seereview_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


@access_action(access_key=get_access_key)
class SeeCinemaReview(SeeReview):
    context = ICinemaReview


@access_action(access_key=get_access_key)
class SeeInterview(SeeReview):
    context = IInterview


def createreview_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Reviewer', ), root=site)#TODO fix roles


class CreateReview(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-file'
    style_order = 3
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = createreview_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        artists, new_artists = extract_artists(
            appstruct.get('artists', []), request)
        newreview = appstruct[OBJECT_DATA]
        root.addtoproperty('reviews', newreview)
        newreview.setproperty('artists', artists)
        newreview.state.append('editable')
        grant_roles(user=user, roles=(('Owner', newreview), ))
        newreview.setproperty('author', user)
        newreview.set_metadata(appstruct)
        newreview.reindex()
        new_objects = new_artists
        new_objects.append(newreview)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {'newcontext': newreview}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


class CreateCinemaReview(CreateReview):
    title = _('Create a cinema review')
    style_picto = 'lac-icon icon-reviwe-cinema'

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        artists, new_artists = extract_artists(
            appstruct.get('artists', []), request)
        directors, new_directors = extract_artists(
            appstruct.get('directors', []),
            request, is_directors=True)
        newreview = appstruct[OBJECT_DATA]
        root.addtoproperty('reviews', newreview)
        newreview.setproperty('artists', artists)
        newreview.setproperty('directors', directors)
        newreview.state.append('editable')
        grant_roles(user=user, roles=(('Owner', newreview), ))
        newreview.setproperty('author', user)
        newreview.set_metadata(appstruct)
        newreview.reindex()
        new_objects = new_artists
        new_objects.extend(new_directors)
        new_objects.append(newreview)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {'newcontext': newreview}


class CreateInterview(CreateReview):
    title = _('Create an interview')
    style_picto = 'lac-icon icon-interview'


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                ('Moderator', site),
                                'Admin'))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def edit_state_validation(process, context):
    if 'editable' in context.state:
        return True

    site = get_site_folder(True)
    return is_site_moderator() or\
           has_role(role=('SiteAdmin', site))


class EditReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IReview
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        artists, new_artists = extract_artists(
            appstruct.get('artists', []), request)
        context.setproperty('artists', artists)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.set_metadata(appstruct)
        if 'published' in context.state:
            not_published_artists = [a for a in context.artists
                                     if 'published' not in a.state]
            for artist in not_published_artists:
                publish_artist(artist, request, user)

        context.reindex()
        new_objects = new_artists
        new_objects.append(context)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class EditCinemaReview(EditReview):
    context = ICinemaReview

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        artists, new_artists = extract_artists(
            appstruct.pop('artists', []), request)
        directors, new_directors = extract_artists(
            appstruct.pop('directors', []),
            request, is_directors=True)
        appstruct.pop('artists_ids')
        appstruct.pop('directors_ids')
        if appstruct.get('picture', None) is not None and \
            OBJECT_DATA in appstruct['picture']:
            appstruct['picture'] = appstruct['picture'][OBJECT_DATA]
            if not getattr(appstruct['picture'], '__name__', None):
                appstruct['picture'].__name__ = 'picture'

        context.set_metadata(appstruct)
        context.set_data(appstruct)
        context.setproperty('artists', artists)
        context.setproperty('directors', directors)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        if 'published' in context.state:
            not_published_artists = [a for a in context.artists
                                     if 'published' not in a.state]
            not_published_artists.extend(
                [a for a in context.directors
                 if 'published' not in a.state])
            for artist in not_published_artists:
                publish_artist(artist, request, user)

        context.reindex()
        new_objects = new_artists
        new_objects.extend(new_directors)
        new_objects.append(context)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {}


class EditInterview(EditReview):
    context = IInterview


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return is_site_moderator() or\
           has_any_roles(roles=(('SiteAdmin', site),
                                'Admin'))


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state


class ArchiveReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return is_site_moderator() or\
           has_any_roles(roles=(('SiteAdmin', site), 'Admin'))


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('reviews', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def submit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), ('SiteAdmin', site)))


def submit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def submit_state_validation(process, context):
    return 'editable' in context.state or \
           'rejected' in context.state


class SubmitReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_class = 'action-success'
    style_order = 1
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = submit_roles_validation
    state_validation = submit_state_validation
    processsecurity_validation = submit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        user = get_current()
        author = getattr(context, 'author', user)
        site_ids = []
        #@TODO Start
        current_site = request.get_site_folder
        sites = [current_site]
        sites.extend(current_site.get_group())
        sites = [s for s in sites
                 if visible_in_site(s, context, request=request)]
        #@TODO End
        for site in sites:#appstruct['sites']:
            site_ids.append(get_oid(site))
            site_services = site.get_all_services(validate=False,
                                                  delegation=False)
            if 'moderation' in site_services:
                moderations = site_services['moderation']
                for moderation in list(set(moderations)):
                    service = moderation.get_unit()
                    service.configure(context, author)
                    service.subscribe(context, author, service=moderation)

        order = update_orders(context, author)
        remove_empty_orders(author)
        is_paid = 'paid' in order.state
        submitted = [context]
        if is_paid:
            context.state = PersistentList(['submitted'])
            submit_review(context)
            submitted.extend(submit_artists(context.artists))
            submitted.extend(
                submit_artists(getattr(context, 'directors', [])))
        else:
            context.state = PersistentList(['to pay'])

        context.sumited_to = PersistentList(site_ids)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, submitted, user))
        return {'is_paid': is_paid}

    def redirect(self, context, request, **kw):
        view = '@@payreview'
        if kw.get('is_paid', False):
            view = '@@index'

        return HTTPFound(request.resource_url(context, view))


def withdraw_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), ('SiteAdmin', site)))


def withdraw_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def withdraw_state_validation(process, context):
    return 'submitted' in context.state or \
           'to pay' in context.state


class WithdrawReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_class = 'action-warning'
    style_order = 2
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = withdraw_roles_validation
    state_validation = withdraw_state_validation
    processsecurity_validation = withdraw_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site_services = context.get_all_services(validate=False,
                                                 delegation=False)
        user = get_current()
        if 'moderation' in site_services:
            author = getattr(context, 'author', user)
            moderations = site_services['moderation']
            for moderation in moderations:
                moderation.unsubscribe(context, author, service=moderation)

            remove_empty_orders(author)

        context.sumited_to = PersistentList([])
        context.state = PersistentList(['editable'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def pay_roles_validation(process, context):
    return has_role(role=('Owner', context))


def pay_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def pay_state_validation(process, context):
    return 'to pay' in context.state


class PayReview(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-credit-card'
    style_order = 3
    submission_title = _('Continue')
    context = IBaseReview
    roles_validation = pay_roles_validation
    state_validation = pay_state_validation
    processsecurity_validation = pay_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        if appstruct.get('paid', True):
            context.state = PersistentList(['submitted'])
            submit_review(context)
            submit_artists(context.artists)
            submit_artists(getattr(context, 'directors', []))
            context.modified_at = datetime.datetime.now(tz=pytz.UTC)
            context.reindex()
            request.registry.notify(ActivityExecuted(self, [context], get_current()))

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


#TODO behaviors
