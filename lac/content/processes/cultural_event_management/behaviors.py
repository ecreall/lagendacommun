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

from dace.util import getSite, get_obj
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
from url_redirector.events import (
    ObjectReplaced, ObjectRemoved)

from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    ICreationCulturelleApplication,
    ICulturalEvent)
from lac.core import access_action, serialize_roles
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.order import Order
from lac.utilities.duplicates_utility import (
    find_duplicates_cultural_events)
from lac.utilities.ical_date_utility import (
    get_publication_periodic_date,
    occurences_start)
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)
from lac.views.filter import visible_in_site
from lac.content.processes.artist_management.behaviors import (
    publish_artist)
from lac.content.processes.venue_management.behaviors import (
    publish_venue, remove_addresses_coordinates)
from lac.utilities.alerts_utility import alert


_marker = object()


def get_duplicates(context):
    return find_duplicates_cultural_events(context, ('published',))


def schedule_expired(context, date=None):
    if date is None:
        date = datetime.datetime.combine(
            datetime.datetime.now(),
            datetime.time(0, 0, 0, tzinfo=pytz.UTC))

    return False if occurences_start(context, 'dates', from_=date) else True


def can_publish_in_periodic(site, context):
    services = site.get_all_services(
        kinds=['extractionservice'],
        delegation=False)
    can_publish = False
    site_publication_date = None
    end_date = None
    has_extraction = 'extractionservice' in services and\
        getattr(services['extractionservice'][0], 'has_periodic', False)
    if has_extraction:
        can_publish, site_publication_date = get_publication_periodic_date(
            site, context)
        if not can_publish:
            end_date = site_publication_date
            site_publication_date = site.next_publication_date()

    return can_publish, site_publication_date, end_date, has_extraction


def extract_artists(artists_data, request, is_directors=False):
    root = request.root
    artists = []
    new_artists = []
    user = get_current()
    if artists_data:
        artists = [a.get(OBJECT_DATA) for a in
                   artists_data if OBJECT_DATA in a]
        new_artists = list(artists)

    for artist in list(artists):
        root.addtoproperty('artists', artist)
        artist.state = PersistentList(['editable'])
        grant_roles(roles=(('Owner', artist), ))
        artist.setproperty('author', user)
        artist.add_contributors([user])
        if is_directors:
            artist.is_director = is_directors

        artist.hash_picture_fp()
        artist.hash_artist_data()
        artist.reindex()
        if getattr(artist, 'origin_oid', None):
            origin = get_obj(artist.origin_oid, None)
            if origin and 'published' not in origin.state:
                replaced = origin.replace_by(artist)
                if replaced:
                    request.registry.notify(ObjectReplaced(
                        old_object=origin,
                        new_object=artist
                    ))
                    root.delfromproperty('artists', origin)

            elif origin:
                if origin.eq(artist):
                    artists.remove(artist)
                    new_artists.remove(artist)
                    artists.append(origin)
                    root.delfromproperty('artists', artist)
                elif artist is not origin:
                    artist.setproperty('original', origin)
                    artist.add_contributors(origin.contributors)

        artist.origin_oid = get_oid(artist)

    return artists, new_artists


def extract_venue(venue_data, request):
    root = request.root
    venue = venue_data.get(OBJECT_DATA, None)
    is_new = True
    result = None
    if venue:
        user = get_current()
        root.addtoproperty('venues', venue)
        venue.state = PersistentList(['editable'])
        grant_roles(roles=(('Owner', venue), ))
        venue.setproperty('author', user)
        venue.add_contributors([user])
        venue.hash_venue_data()
        venue.reindex()
        result = venue
        if getattr(venue, 'origin_oid', None):
            origin = get_obj(venue.origin_oid, None)
            if origin:
                if 'published' not in origin.state:
                    replaced = origin.replace_by(venue)
                    if replaced:
                        request.registry.notify(ObjectReplaced(
                            old_object=origin,
                            new_object=venue
                        ))
                        root.delfromproperty('venues', origin)
                else:
                    if origin.eq(venue):
                        result = origin
                        is_new = False
                        root.delfromproperty('venues', venue)
                    elif venue is not origin:
                        venue.setproperty('original', origin)
                        venue.add_contributors(origin.contributors)

        venue.origin_oid = get_oid(venue)

    return result, is_new


def group_venues(new_venues, request):
    root = request.root
    validate_venues = []
    for venue in new_venues:
        if venue not in validate_venues:
            venues = list(new_venues)
            venues.remove(venue)
            eq_venues = [v for v in
                         venues if v.eq(venue)]
            if eq_venues:
                validate_venues.extend(eq_venues)
                validate_venues.append(venue)
                for eq_venue in venues:
                    replaced = eq_venue.replace_by(venue)
                    if replaced:
                        request.registry.notify(ObjectReplaced(
                            old_object=eq_venue,
                            new_object=venue
                        ))
                        root.delfromproperty('venues', eq_venue)


def submit_artists(artists):
    submited = []
    for artist in artists:
        if 'editable' in artist.state or \
           'rejected' in artist.state:
            artist.state = PersistentList(['submitted'])
            artist.reindex()
            submited.append(artist)

    return submited


def submit_venues(venues):
    submited = []
    for venue in venues:
        if 'editable' in venue.state or \
           'rejected' in venue.state:
            venue.state = PersistentList(['submitted'])
            venue.reindex()
            submited.append(venue)

    return submited


def submit_cultural_event(context):
    #TODO submit and duplicate the event
    pass


def update_orders(context, author):
    services = context.get_all_services(validate=False, delegation=False)
    unpaid = [[s for s in services[service]
               if s.order is None or 'unpaid' in s.order.state]
              for service in services]
    unpaid = list(set([item for sublist in unpaid for item in sublist]))
    order = Order()
    if getattr(author, 'customeraccount', _marker) is None:
        author.add_customeraccount()

    customeraccount = getattr(author, 'customeraccount', None)
    if customeraccount:
        customeraccount.addtoproperty('orders', order)

    for service in unpaid:
        if service.order:
            service.delfromproperty('order', service.order)

        order.addtoproperty('products', service)

    if order.total <= 0 or customeraccount is None:
        order.state.append('paid')
    else:
        order.state.append('unpaid')

    return order


def remove_empty_orders(author):
    for cuorder in list(author.customeraccount.orders):
        if not cuorder.products:
            author.customeraccount.delfromproperty('orders', cuorder)


def send_creation_mails(context, request, author):
    site = request.get_site_folder
    mail_template = site.get_mail_template('registration_confirmation')
    subject = mail_template['subject'].format()
    mail = mail_template['template'].format()
    sender = site.get_site_sender()
                # member=getattr(author, 'name', ''),
                # url=request.resource_url(cultural_event, '@@index'))
    alert('email', [sender], [author.email],
          {'subject': subject, 'body': mail})
    if getattr(context, 'selling_tickets', False):
        mail_template = site.get_mail_template('selling_tickets')
        subject = mail_template['subject'].format()
        mail = mail_template['template'].format()
        alert('email', [sender], [author.email],
              {'subject': subject, 'body': mail})


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        result = serialize_roles(
            (('Owner', obj), 'SiteAdmin', 'Moderator'))
        return result


def seeculturalcvent_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                ('Moderator', site)))


@access_action(access_key=get_access_key)
class SeeCulturalEvent(InfiniteCardinality):
    """SeeFile is the behavior allowing access to context"""
    title = _('Details')
    context = ICulturalEvent
    actionType = ActionType.automatic
    processsecurity_validation = seeculturalcvent_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def create_roles_validation(process, context):
    return has_role(role=('Member',))


def create_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class CreateCulturalEvent(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'lac-icon icon-bullhorn'
    style_order = 0
    submission_title = _('Save')
    title = _('Announce a cultural event')
    unavailable_link = 'docanonymous'
    context = ICreationCulturelleApplication
    roles_validation = create_roles_validation
    processsecurity_validation = create_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        author = get_current()
        artists, new_artists = extract_artists(
            appstruct.pop('artists', []), request)
        appstruct.pop('artists_ids')
        schedules = []
        new_venues = []
        for schedule_data in appstruct['schedules']:
            schedule = schedule_data[OBJECT_DATA]
            venue_data = schedule_data.get('venue', None)
            if venue_data:
                venue, is_new = extract_venue(venue_data, request)
                if is_new:
                    new_venues.append(venue)

                schedule.setproperty('venue', venue)

            schedules.append(schedule)

        cultural_event = appstruct[OBJECT_DATA]
        cultural_event.setproperty('schedules', [])
        root.addtoproperty('cultural_events', cultural_event)
        for schedule in schedules:
            schedule.state = PersistentList(['created'])
            root.addtoproperty('schedules', schedule)
            cultural_event.addtoproperty('schedules', schedule)
            schedule.reindex_dates()
            if schedule_expired(schedule):
                schedule.state.append('archived')
                schedule.reindex()

        group_venues(new_venues, request)
        cultural_event.state.append('editable')
        grant_roles(roles=(('Owner', cultural_event), ))
        cultural_event.setproperty('author', author)
        cultural_event.add_contributors([author])
        cultural_event.setproperty('artists', artists)
        cultural_event.set_metadata(appstruct)
        cultural_event.reindex()
        send_creation_mails(cultural_event, request, author)
        new_objects = new_venues
        new_objects.extend(new_artists)
        new_objects.append(cultural_event)
        request.registry.notify(ActivityExecuted(self, new_objects, author))
        return {'newcontext': cultural_event}

    def redirect(self, context, request, **kw):
        newcontext = kw['newcontext']
        duplicates = get_duplicates(newcontext)
        if duplicates:
            view = '@@potentialduplicatesculturalevent'
        else:
            view = '@@index'

        return HTTPFound(request.resource_url(newcontext, view))


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
    return has_role(role=('SiteAdmin', site)) or\
           is_site_moderator()


class EditCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = ICulturalEvent
    roles_validation = edit_roles_validation
    state_validation = edit_state_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        user = get_current()
        appstruct.pop('_csrf_token_')
        artists, new_artists = extract_artists(
            appstruct.pop('artists', []), request)
        appstruct.pop('artists_ids')
        schedules = []
        new_venues = []
        for schedule_data in appstruct['schedules']:
            schedule = schedule_data[OBJECT_DATA]
            venue_data = schedule_data.get('venue', None)
            if venue_data:
                venue, is_new = extract_venue(venue_data, request)
                if is_new:
                    new_venues.append(venue)

                schedule.setproperty('venue', venue)

            schedules.append(schedule)

        appstruct['schedules'] = schedules
        schedules_to_remove = [s for s in context.schedules
                               if s not in appstruct['schedules']]
        for schedule in appstruct['schedules']:
            schedule.state = PersistentList(['created'])
            if not getattr(schedule, '__parent__', None):
                root.addtoproperty('schedules', schedule)

            schedule.reindex_dates()
            if schedule_expired(schedule):
                schedule.state.append('archived')
                schedule.reindex()

        group_venues(new_venues, request)
        if 'picture' in appstruct and appstruct['picture'] and \
            OBJECT_DATA in appstruct['picture']:
            appstruct['picture'] = appstruct['picture'][OBJECT_DATA]
            if not getattr(appstruct['picture'], '__name__', None):
                appstruct['picture'].__name__ = 'picture'

        context.set_metadata(appstruct)
        context.set_data(appstruct)
        for schedule in schedules_to_remove:
            root.delfromproperty('schedules', schedule)

        context.setproperty('artists', artists)
        #context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        remove_addresses_coordinates(new_venues)
        if 'published' in context.state:
            not_published_venues = [s.venue for s in context.schedules
                                    if s.venue and 'published' not in s.venue.state]
            for venue in not_published_venues:
                publish_venue(venue, request, user)

            not_published_artists = [a for a in context.artists
                                     if 'published' not in a.state]
            for artist in not_published_artists:
                publish_artist(artist, request, user)

        context.reindex()
        new_objects = new_venues
        new_objects.extend(new_artists)
        new_objects.append(context)
        request.registry.notify(ActivityExecuted(self, new_objects, user))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def pay_roles_validation(process, context):
    return has_role(role=('Owner', context))


def pay_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def pay_state_validation(process, context):
    return 'to pay' in context.state


class PayCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-credit-card'
    style_order = 3
    submission_title = _('Continue')
    context = ICulturalEvent
    roles_validation = pay_roles_validation
    state_validation = pay_state_validation
    processsecurity_validation = pay_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        if appstruct.get('paid', True):
            context.state = PersistentList(['submitted'])
            submit_artists(context.artists)
            submit_venues([s.venue for s in context.schedules if s.venue])
            submit_cultural_event(context)
            context.modified_at = datetime.datetime.now(tz=pytz.UTC)
            context.reindex()
            request.registry.notify(ActivityExecuted(
                self, [context], get_current()))

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def archive_roles_validation(process, context):
    site = get_site_folder(True)
    return is_site_moderator() or\
           has_role(role=('SiteAdmin', site))


def archive_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def archive_state_validation(process, context):
    return 'published' in context.state or \
           'editable' in context.state


class ArchiveCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 6
    submission_title = _('Continue')
    context = ICulturalEvent
    roles_validation = archive_roles_validation
    state_validation = archive_state_validation
    processsecurity_validation = archive_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        #TODO archived
        context.state = PersistentList(['archived'])
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, [context], get_current()))
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def duppublication_roles_validation(process, context):
    return has_role(role=('Member',))


def duppublication_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


def duppublication_state_validation(process, context):
    return 'published' in context.state


class DuplicateCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-resize-full'
    style_order = 2
    submission_title = _('Save')
    context = ICulturalEvent
    roles_validation = duppublication_roles_validation
    processsecurity_validation = duppublication_processsecurity_validation
    state_validation = duppublication_state_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        author = get_current()
        artists, new_artists = extract_artists(
            appstruct.pop('artists', []), request)
        appstruct.pop('artists_ids')
        schedules = []
        new_venues = []
        for schedule_data in appstruct['schedules']:
            schedule = schedule_data[OBJECT_DATA]
            venue_data = schedule_data.get('venue', None)
            if venue_data:
                venue, is_new = extract_venue(venue_data, request)
                if is_new:
                    new_venues.append(venue)

                schedule.setproperty('venue', venue)

            schedules.append(schedule)

        cultural_event = appstruct[OBJECT_DATA]
        cultural_event.setproperty('schedules', [])
        root.addtoproperty('cultural_events', cultural_event)
        for schedule in schedules:
            schedule.state = PersistentList(['created'])
            root.addtoproperty('schedules', schedule)
            cultural_event.addtoproperty('schedules', schedule)
            schedule.reindex_dates()
            if schedule_expired(schedule):
                schedule.state.append('archived')
                schedule.reindex()

        group_venues(new_venues, request)
        cultural_event.state.append('editable')
        grant_roles(roles=(('Owner', cultural_event), ))
        cultural_event.setproperty('original', context)
        cultural_event.setproperty('author', author)
        cultural_event.addtoproperty('contributors', author)
        cultural_event.add_contributors(context.contributors)
        cultural_event.addtoproperty('contributors', author)
        remove_addresses_coordinates(new_venues)
        cultural_event.setproperty('artists', artists)
        cultural_event.set_metadata(appstruct)
        cultural_event.reindex()
        send_creation_mails(cultural_event, request, author)
        source = request.GET.get('source', '')
        if source:
            source_culturalevent = get_obj(int(source))
            if source_culturalevent:
                root.delfromproperty('cultural_events',
                                     source_culturalevent)

        new_objects = new_venues
        new_objects.extend(new_artists)
        new_objects.append(cultural_event)
        request.registry.notify(ActivityExecuted(self, new_objects, author))
        return {'newcontext': cultural_event}

    def redirect(self, context, request, **kw):
        newcontext = kw['newcontext']
        if 'published' in context.state:
            duplicates = get_duplicates(newcontext)
            if duplicates:
                view = '@@potentialduplicatesculturalevent'
            else:
                view = '@@index'

            return HTTPFound(request.resource_url(newcontext, view))

        return HTTPFound(request.resource_url(newcontext, "@@index"))


def submit_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context), ('SiteAdmin', site)))


def submit_processsecurity_validation(process, context):
    return not schedule_expired(context) and \
           global_user_processsecurity(process, context)


def submit_state_validation(process, context):
    return 'editable' in context.state


class SubmitCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-share'
    style_class = 'action-success'
    style_order = 1
    submission_title = _('Continue')
    context = ICulturalEvent
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
        # can_publish_data = can_publish_in_periodic(current_site, context)
        # can_publish = can_publish_data[0]
        # has_extraction = can_publish_data[3]
        # if can_publish or not has_extraction:
        mail_template = current_site.get_mail_template('validation_confirmation')
        subject = mail_template['subject'].format()
        mail = mail_template['template'].format(
                    member=getattr(author, 'name', ''),
                    url=request.resource_url(context, '@@index'))
        alert('email', [current_site.get_site_sender()], [author.email],
              {'subject': subject, 'body': mail})

        # elif has_extraction:
        #     mail_template = current_site.get_mail_template('validation_confirmation_date')
        #     subject = mail_template['subject'].format()
        #     mail = mail_template['template'].format(
        #                 member=getattr(author, 'name', ''),
        #                 url=request.resource_url(context, '@@index'))
        #     mailer_send(subject=subject, body=mail,
        #                 recipients=[author.email],
        #                 sender=current_site.get_site_sender())
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
        submited_objects = [context]
        if is_paid:
            context.state = PersistentList(['submitted'])
            submit_cultural_event(context)
            submited_objects.extend(submit_artists(context.artists))
            submited_objects.extend(
                submit_venues([s.venue for s in context.schedules if s.venue]))
        else:
            context.state = PersistentList(['to pay'])

        context.sumited_to = PersistentList(site_ids)
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.reindex()
        request.registry.notify(ActivityExecuted(self, submited_objects, user))
        return {'is_paid': is_paid}

    def redirect(self, context, request, **kw):
        view = '@@payculturalevent'
        if kw.get('is_paid', False):
            view = '@@index'

        return HTTPFound(request.resource_url(context, view))


def withdraw_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Owner', context),
                                ('SiteAdmin', site),
                                'Admin'))


def withdraw_processsecurity_validation(process, context):
    #@TODO si pas de version publiee
    return global_user_processsecurity(process, context)


def withdraw_state_validation(process, context):
    return 'submitted' in context.state or \
           'to pay' in context.state


class WithdrawCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_picto = 'glyphicon glyphicon-step-backward'
    style_class = 'action-warning'
    style_order = 2
    submission_title = _('Continue')
    context = ICulturalEvent
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


def remove_roles_validation(process, context):
    site = get_site_folder(True)
    return ('editable' in context.state and \
            has_role(role=('Owner', context))) or \
           is_site_moderator() or\
           has_any_roles(roles=(('SiteAdmin', site),
                                'Admin'))


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveCulturalEvent(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-trash'
    style_order = 7
    submission_title = _('Continue')
    context = ICulturalEvent
    roles_validation = remove_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        for schedule in context.schedules:
            context.delfromproperty('schedules', schedule)
            root.delfromproperty('schedules', schedule)

        root.delfromproperty('cultural_events', context)
        request.registry.notify(ObjectRemoved(
            obj=context,
            parent=root
        ))
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


def managedup_state_validation(process, context):
    return 'archived' not in context.state and \
           'rejected' not in context.state


def managedup_processsecurity_validation(process, context):
    return get_duplicates(context) and \
        global_user_processsecurity(process, context)


class ManageDuplicates(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'body-action'
    style_picto = 'octicon octicon-git-compare'
    style_order = 8
    template = 'lac:views/templates/manage_duplicates.pt'
    submission_title = _('Abandon')
    context = ICulturalEvent
    roles_validation = remove_roles_validation
    processsecurity_validation = managedup_processsecurity_validation
    state_validation = managedup_state_validation

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))

#TODO behaviors
