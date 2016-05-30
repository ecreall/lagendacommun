# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.threadlocal import get_current_request

from dace.objectofcollaboration.principal.util import get_current

from lac.utilities.utils import get_site_folder


def service_validation(process, context):

    site = get_site_folder(True)
    site_service = process.execution_context.get_involved_entity('site')
    if site is not site_service:
        return False

    service = process.execution_context.get_involved_entity('service')
    if not service:
        return False

    if getattr(context, 'is_imported', False):
        return True

    user = get_current()
    context_service = context.get_all_services(
        kinds=['moderation'],
        validate=True,
        delegation=False).get('moderation', None)
    is_valid = service.is_valid(site, user) and service.delegated_to(user)
    return is_valid and \
           (context_service or \
            (context_service is None and \
             user is getattr(context, 'author', None)))


def is_site_moderator(request=None):
    if request is None:
        request = get_current_request()

    return request.is_site_moderator
