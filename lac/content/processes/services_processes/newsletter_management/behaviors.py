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
    has_any_roles)
from dace.interfaces import IEntity
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from lac.content.processes.user_management.behaviors import (
    global_user_processsecurity as base_global_user_processsecurity)
from lac.content.interface import (
    ICreationCulturelleApplication,
    INewsletter)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import (
    get_site_folder, gen_random_token)
from lac.utilities.alerts_utility import alert


def nl_service_processsecurity(process, context):
    site = get_site_folder(True)
    services = site.get_all_services(
        kinds=['newsletterservice'],
        validate=True,
        delegation=False)
    return services.get('newsletterservice', [])


def global_user_processsecurity(process, context):
    return nl_service_processsecurity(process, context) and\
        base_global_user_processsecurity(process, context)


def send_newsletter_content(newsletter, request):
    site = newsletter.site
    subject = getattr(newsletter, 'subject', newsletter.title)
    mail_template = newsletter.content
    sender = site.get_site_sender()
    for (key, user_data) in newsletter.subscribed.items():
        email = user_data.get('email', None)
        if email and site:
            root = site.__parent__
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            url = request.resource_url(
                root, '@@userunsubscribenewsletter',
                query={'oid': get_oid(newsletter),
                       'user': key+'@@'+user_data.get('id', '')})
            mail = mail_template.format(
                first_name=first_name,
                last_name=last_name,
                newsletter_title=newsletter.title,
                unsubscribeurl=url)
            alert('email', [sender], [email],
                  {'subject': subject, 'html': mail})

    now = datetime.datetime.now(tz=pytz.UTC)
    newsletter.annotations.setdefault(
        'newsletter_history', PersistentList()).append(
        {'date': now,
         'subject': subject,
         'content': newsletter.content
        })
    newsletter.content = newsletter.get_content_template()
    if getattr(newsletter, 'recurrence', False):
        newsletter.sending_date = newsletter.get_next_sending_date(now)


def get_access_key(obj):
    result = serialize_roles(('NewsletterResponsible', 'Admin'))
    return result


def seenewsletter_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('NewsletterResponsible', site), 'Admin'))


@access_action(access_key=get_access_key)
class SeeNewsletter(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = INewsletter
    actionType = ActionType.automatic
    processsecurity_validation = seenewsletter_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def createnewsletter_roles_validation(process, context):
    site = get_site_folder(True)
    return has_role(role=('Advertiser', ), root=site)


def createnewsletter_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class CreateNewsletter(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-envelope'
    style_order = 5
    title = _('Create a newsletter')
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = createnewsletter_roles_validation
    processsecurity_validation = createnewsletter_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site = get_site_folder(True)
        newnewsletter = appstruct['_object_data']
        site.addtoproperty('newsletters', newnewsletter)
        newnewsletter.reset_content()
        newnewsletter.reindex()
        return {'newcontext': newnewsletter}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(kw['newcontext'], "@@index"))


def edit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(
        roles=('NewsletterResponsible', 'Admin'), root=site)


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = INewsletter
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reset_content()
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class ConfigureRecNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-repeat'
    style_order = 2
    submission_title = _('Save')
    context = INewsletter
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.sending_date = datetime.datetime.combine(
            context.sending_date,
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class RedactNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-align-left'
    style_order = 2
    submission_title = _('Save')
    context = INewsletter
    roles_validation = edit_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reset_content()
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def send_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('NewsletterResponsible', 'Admin'), root=site)


def send_processsecurity_validation(process, context):
    return context.can_send() and \
           global_user_processsecurity(process, context)


class SendNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-send'
    style_order = 1
    submission_title = _('Continue')
    context = INewsletter
    roles_validation = send_roles_validation
    processsecurity_validation = send_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        send_newsletter_content(context, request)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('NewsletterResponsible', 'Admin'), root=site)


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_interaction = 'modal-action'
    style_order = 10
    submission_title = _('Continue')
    context = INewsletter
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        site = get_site_folder(True)
        site.delfromproperty('newsletters', context)
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def subscribe_roles_validation(process, context):
    return has_any_roles(roles=('Anonymous', 'Member'))


def subscribe_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return site.newsletters and\
        nl_service_processsecurity(process, context)


class SubscribeNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'footer-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-envelope'
    style_order = 4
    submission_title = _('Save')
    context = IEntity
    roles_validation = subscribe_roles_validation
    processsecurity_validation = subscribe_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        email = appstruct.pop('email')
        newnewsletters = appstruct.pop('newsletters')
        first_name = appstruct.get('first_name')
        last_name = appstruct.get('last_name')
        random_key = gen_random_token()
        key = email
        user_data = {'first_name': first_name,
                     'last_name': last_name,
                     'email': email,
                     'id': random_key,
                     'title': first_name+' '+\
                        last_name}
        site = get_site_folder(True)
        mail_template = site.get_mail_template('newsletter_subscription')
        for newsletter in newnewsletters:
            newsletter.subscribed[key] = user_data
            url = request.resource_url(
                context, '@@userunsubscribenewsletter',
                query={'oid': get_oid(newsletter),
                       'user': key+'@@'+random_key})
            subject = mail_template['subject'].format(
                newsletter_title=newsletter.title)
            mail = mail_template['template'].format(
                first_name=first_name,
                last_name=last_name,
                newsletter_title=newsletter.title,
                unsubscribeurl=url)
            alert('email', [site.get_site_sender()], [email],
                  {'subject': subject, 'body': mail})

        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def userunsubscribe_roles_validation(process, context):
    return has_any_roles(roles=('Anonymous', 'Member'))


class UserUnsubscribeNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-ok'
    style_order = 5
    submission_title = _('Continue')
    context = ICreationCulturelleApplication
    roles_validation = userunsubscribe_roles_validation

    def start(self, context, request, appstruct, **kw):
        newsletter = appstruct.pop('newsletter')
        user = appstruct.pop('user', None)
        if user:
            parts = user.split('@@')
            key = parts[0]
            user_id = parts[1]
            subscribed = newsletter.subscribed.get(key, None)
            if subscribed and user_id == subscribed.get('id', None):
                newsletter.subscribed.pop(key)
                first_name = subscribed.get('first_name')
                last_name = subscribed.get('last_name')
                email = subscribed.get('email')
                site = get_site_folder(True)
                mail_template = site.get_mail_template('newsletter_unsubscription')
                subject = mail_template['subject'].format(
                    newsletter_title=newsletter.title)
                mail = mail_template['template'].format(
                    first_name=first_name,
                    last_name=last_name,
                    newsletter_title=newsletter.title)
                alert('email', [site.get_site_sender()], [email],
                      {'subject': subject, 'body': mail})

        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def unsubscribe_processsecurity_validation(process, context):
    return base_global_user_processsecurity(process, context)


def unsubscribe_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('NewsletterResponsible', 'Admin'), root=site)


class UnsubscribeNewsletter(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'typcn typcn-user-delete'
    style_order = 5
    submission_title = _('Continue')
    context = INewsletter
    roles_validation = unsubscribe_roles_validation
    processsecurity_validation = unsubscribe_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        email = appstruct.pop('email')
        key = email
        subscribed = context.subscribed.get(key, None)
        if subscribed:
            context.subscribed.pop(key)
            first_name = subscribed.get('first_name')
            last_name = subscribed.get('last_name')
            email = subscribed.get('email')
            site = get_site_folder(True)
            mail_template = site.get_mail_template('newsletter_unsubscription')
            subject = mail_template['subject'].format(
                newsletter_title=context.title)
            mail = mail_template['template'].format(
                first_name=first_name,
                last_name=last_name,
                newsletter_title=context.title)
            alert('email', [site.get_site_sender()], [email],
                  {'subject': subject, 'body': mail})

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def see_all_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=('NewsletterResponsible', 'Admin'), root=site)


def see_all_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return site.newsletters and base_global_user_processsecurity(process, context)


class SeeNewsletters(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-envelope'
    style_order = 4.5
    submission_title = _('Continue')
    context = ICreationCulturelleApplication
    roles_validation = see_all_roles_validation
    processsecurity_validation = see_all_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def see_subscribed_processsecurity_validation(process, context):
    return context.subscribed and base_global_user_processsecurity(process, context)


class SeeSubscribed(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'ion-person-stalker'
    style_order = 4
    context = INewsletter
    roles_validation = see_all_roles_validation
    processsecurity_validation = see_subscribed_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class SeeNewsletterHistory(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'footer-entity-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-time'
    title = _('Content history')
    style_order = 2
    isSequential = False
    context = INewsletter
    processsecurity_validation = seenewsletter_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

#TODO behaviors
