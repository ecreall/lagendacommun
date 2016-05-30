# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import datetime
import pytz
import transaction
import io
from pyramid.response import FileIter
from pyramid.httpexceptions import HTTPFound


from dace.processinstance.core import Behavior
from dace.util import getSite
from dace.objectofcollaboration.principal.util import (
    has_any_roles)
from dace.processinstance.activity import (
    InfiniteCardinality,
    ActionType)

from lac import log, _, CLASSIFICATIONS
from ..user_management.behaviors import global_user_processsecurity
from lac.content.interface import (
    IFilmSchedule, ICreationCulturelleApplication)
from lac.core import access_action, serialize_roles
from lac.utilities.cinema_utility import (
    get_cineam_schedules, dates_to_fr_date, get_schedules)
from lac.utilities.utils import get_site_folder
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)
from lac.content.smart_folder import generate_search_smart_folder


def get_access_key(obj):
    if 'published' in obj.state:
        return ['always']
    else:
        return serialize_roles(('SiteAdmin', 'Journalist', 'Moderator'))


def see_processsecurity_validation(process, context):
    site = get_site_folder(True)
    return 'published' in context.state or \
           has_any_roles(roles=(('SiteAdmin', site), ('Moderator', site),
                                ('Journalist', site)))


@access_action(access_key=get_access_key)
class SeeFilmSchedule(InfiniteCardinality):
    """SeeFilmSchedule is the behavior allowing access to context"""
    title = _('Details')
    context = IFilmSchedule
    actionType = ActionType.automatic
    processsecurity_validation = see_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def admin_roles_validation(process, context):
    site = get_site_folder(True)
    return has_any_roles(roles=(('Journalist', site),
                                ('SiteAdmin', site),
                                'Admin')) or\
           is_site_moderator()


class AddCinemagoer(InfiniteCardinality):
    style_descriminator = 'admin-action'
    style_picto = 'glyphicon glyphicon-film'
    style_order = 1
    submission_title = _('Save')
    context = ICreationCulturelleApplication
    roles_validation = admin_roles_validation

    def start(self, context, request, appstruct, **kw):
        schedules = appstruct['venues']
        next_date = dates_to_fr_date(appstruct['next_date'])
        root = getSite()
        for venue_data in schedules:
            venue = venue_data['title']
            old_schedules = get_cineam_schedules(venue)
            for old_obj in old_schedules.get(venue, []):
                root.delfromproperty('film_schedules', old_obj)

            schedules_objs = get_schedules(
                venue_data['schedules'], venue, next_date)
            for obj in schedules_objs:
                root.addtoproperty('film_schedules', obj)
                obj.reindex()

        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, ""))


def edit_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class EditFilmSchedule(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'text-action'
    style_picto = 'glyphicon glyphicon-pencil'
    style_order = 1
    submission_title = _('Save')
    context = IFilmSchedule
    roles_validation = admin_roles_validation
    processsecurity_validation = edit_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        context.modified_at = datetime.datetime.now(tz=pytz.UTC)
        context.set_metadata(appstruct)
        context.reindex()
        return {}

    def redirect(self, context, request, **kw):
        return HTTPFound(request.resource_url(context, "@@index"))


def remove_processsecurity_validation(process, context):
    return global_user_processsecurity(process, context)


class RemoveFilmSchedule(InfiniteCardinality):
    style = 'button' #TODO add style abstract class
    style_descriminator = 'global-action'
    style_interaction = 'modal-action'
    style_picto = 'glyphicon glyphicon-folder-close'
    style_order = 7
    submission_title = _('Continue')
    context = IFilmSchedule
    roles_validation = admin_roles_validation
    processsecurity_validation = remove_processsecurity_validation

    def start(self, context, request, appstruct, **kw):
        root = getSite()
        root.delfromproperty('film_schedules', context)
        return {}

    def redirect(self, context, request, **kw):
        root = getSite()
        return HTTPFound(request.resource_url(root, ""))


class ExtractSchedules(Behavior):
    behavior_id = "extract"
    title = _("Extract")
    description = ""

    def start(self, context, request, appstruct, **kw):
        odtfile = io.BytesIO()
        try:
            if appstruct:
                schedules = appstruct['venues']
                next_date = dates_to_fr_date(appstruct['next_date'])
                schedules_objs = []
                for venue_data in schedules:
                    venue = venue_data['title']
                    schedules_objs.extend(get_schedules(
                        venue_data['schedules'], venue, next_date))

                source_class = None
                classifications = (CLASSIFICATIONS['venue_classification'],
                                   CLASSIFICATIONS['city_classification'])
                for classification in classifications:
                    source_class = classification(source_class)

                folder = generate_search_smart_folder('Extraction folder')
                folder.classifications = source_class
                odtfile = folder.classifications.extract(
                    schedules_objs, request, folder,
                    template_type="extraction")
                transaction.abort()
        except Exception as error:
            log.warning(error)

        return {'odtfile': odtfile}

    def redirect(self, context, request, **kw):
        odtfile = kw.get('odtfile', io.BytesIO())
        file_name = 'Extraction_cinema'
        response = request.response
        response.content_type = 'application/vnd.oasis.opendocument.text'
        response.content_disposition = 'inline; filename="{file_name}.odt"'.format(
            file_name=file_name)
        response.app_iter = FileIter(odtfile)
        return response

#TODO behaviors
