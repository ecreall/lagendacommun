# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
from persistent.list import PersistentList
from pyramid.httpexceptions import HTTPFound

from dace.util import find_catalog, getSite, get_obj
from dace.objectofcollaboration.principal.util import (
    has_role, get_current)
from dace.processinstance.activity import (
    ElementaryAction,
    ActionType)
from dace.processinstance.core import ActivityExecuted

from lac.content.processes.services_processes.\
    newsletter_management.behaviors import send_newsletter_content
from lac.content.interface import (
    ICreationCulturelleApplication,
    ICulturalEvent,
    ISchedule,
    IService,
    IAlert)
from lac.views.filter import find_entities
from lac import log
from lac.content.alert import InternalAlertKind
from lac.utilities.alerts_utility import alert
from lac.content.site_folder import SiteFolder


ALERT_DURATION = 20


DAYS_BEFORE_ALERT = 2


def system_roles_validation(process, context):
    return has_role(role=('System', ))


class ArchiveCulturalEvent(ElementaryAction):
    context = ICreationCulturelleApplication
    actionType = ActionType.system
    roles_validation = system_roles_validation

    def start(self, context, request, appstruct, **kw):
        all_archived = []
        lac_catalog = find_catalog('lac')
        start_date = datetime.datetime.combine(
            datetime.datetime.now(),
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))
        start_date_index = lac_catalog['start_date']
        query = start_date_index.notinrange(start_date, None)
        events_toarchive = find_entities(
            interfaces=[ICulturalEvent],
            metadata_filter={'states': ['published']},
            add_query=query)
        for event in events_toarchive:
            event.state = PersistentList(['archived'])
            event.modified_at = datetime.datetime.now(tz=pytz.UTC)
            event.reindex()
            all_archived.append(event)

        dace_catalog = find_catalog('dace')
        states_index = dace_catalog['object_states']
        object_provides_index = dace_catalog['object_provides']
        query = start_date_index.notinrange(start_date, None) &\
            states_index.any(['none', 'created']) &\
            object_provides_index.any([ISchedule.__identifier__])
        schedules_toarchive = query.execute()
        for schedule in schedules_toarchive:
            schedule.state = PersistentList(['archived'])
            schedule.modified_at = datetime.datetime.now(tz=pytz.UTC)
            schedule.reindex()
            all_archived.append(schedule)

        request.registry.notify(ActivityExecuted(
            self, all_archived, get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class SynchronizePublishSettings(ElementaryAction):
    context = ICreationCulturelleApplication
    actionType = ActionType.system
    roles_validation = system_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        sites = root.site_folders
        now = datetime.datetime.combine(
            datetime.datetime.utcnow(),
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))
        for site in sites:
            #TODO Synchronize Publish Settings
            if hasattr(site, 'closing_date'):
                closing_date = site.closing_date.replace(tzinfo=pytz.UTC)
                if now >= closing_date:
                    site.publication_number += 1
                    site.closing_date += datetime.timedelta(
                        days=site.closing_frequence)
                    log.warning('Synchronize Publish Settings')

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class AlertUsers(ElementaryAction):
    context = ICreationCulturelleApplication
    actionType = ActionType.system
    roles_validation = system_roles_validation

    def start(self, context, request, appstruct, **kw):
        lac_catalog = find_catalog('lac')
        subscription_kind_index = lac_catalog['subscription_kind']
        now = datetime.datetime.combine(
            datetime.datetime.utcnow(),
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))
        #remove old alerts
        created_before = now - datetime.timedelta(days=ALERT_DURATION)
        created_at_index = lac_catalog['created_at']
        date_query = created_at_index.lt(created_before)
        old_alerts = find_entities(
            interfaces=[IAlert],
            add_query=date_query)
        for old_alert in old_alerts:
            if old_alert.__parent__:
                old_alert.__parent__.delfromproperty('alerts', old_alert)

        #alert services
        query = subscription_kind_index.any(['subscription'])
        services = find_entities(
            interfaces=[IService],
            add_query=query)
        for service in services:
            customer = getattr(getattr(service, 'customer', None), 'user', None)
            perimeter = getattr(service, 'perimeter', None)
            site = perimeter if isinstance(perimeter, SiteFolder) else None
            if not site:
                site_oid = getattr(service, 'source_site', None)
                if site_oid:
                    site = get_obj(site_oid)

            if customer and site:
                is_expired = service.is_expired()
                end_date = getattr(service, 'end_date', None)
                alert_date = (end_date - datetime.timedelta(
                    days=DAYS_BEFORE_ALERT)).replace(tzinfo=pytz.UTC)
                all_alerts = customer.all_alerts
                old_alerts_expired = customer.get_alerts(
                    all_alerts,
                    kind=InternalAlertKind.service_alert,
                    subject=service, **{'alert_kind': 'expired'})
                old_alerts_deadline = customer.get_alerts(
                    all_alerts,
                    kind=InternalAlertKind.service_alert,
                    subject=service, **{'alert_kind': 'deadline'})
                if is_expired:
                    #alert if is expired
                    if not old_alerts_expired:
                        alert('internal', [site], [customer],
                              {'kind': InternalAlertKind.service_alert,
                               'subjects': [service],
                               'alert_kind': 'expired'})

                elif end_date and now >= alert_date:
                    if not old_alerts_deadline:
                        alert('internal', [site], [customer],
                              {'kind': InternalAlertKind.service_alert,
                               'subjects': [service],
                               'alert_kind': 'deadline'})

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


class SendNewsletters(ElementaryAction):
    context = ICreationCulturelleApplication
    actionType = ActionType.system
    roles_validation = system_roles_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        sites = root.site_folders
        now = datetime.datetime.combine(
            datetime.datetime.utcnow(),
            datetime.time(23, 59, 59, tzinfo=pytz.UTC))
        for site in sites:
            automatic_newsletters = [n for n in site.newsletters
                                     if getattr(n, 'recurrence', False) and
                                     now >= n.get_sending_date() and
                                     n.can_send()]
            for newsletter in automatic_newsletters:
                send_newsletter_content(newsletter, request)
                log.info('Send: '+site.title+'->'+newsletter.title)

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


#TODO behaviors
