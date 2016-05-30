# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import os
import transaction
from persistent.list import PersistentList
from pyramid.events import ApplicationCreated, subscriber
from pyramid.request import Request
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import manager

from substanced.event import RootAdded, ObjectRemoved
from substanced.util import find_service

from url_redirector import add_storage_to_root
from lac.views.filter import (
    get_alerts_by_subject)
from lac import core
from lac.content.site_folder import SiteFolder
from lac import DEFAULT_SITE_ID
from lac.utilities.social_login import init_sites_social_login


@subscriber(RootAdded)
def mysubscriber(event):
    """Add the lac catalog when the root is added."""
    root = event.object
    registry = get_current_registry()
    settings = registry.settings
    lac_title = settings.get('lac.title')
    root.title = lac_title
    catalogs = find_service(root, 'catalogs')
    catalogs.add_catalog('lac')
    default_site = SiteFolder(title="Création culturelle")
    default_site.urls_ids = PersistentList(DEFAULT_SITE_ID)
    root.addtoproperty('site_folders', default_site)
    add_storage_to_root(root, registry)
    root.default_site = default_site


@subscriber(ApplicationCreated)
def add_services_definitions(event):
    app = event.object
    registry = app.registry
    settings = getattr(registry, 'settings', {})
    request = Request.blank('/application_created') # path is meaningless
    request.registry = registry
    manager.push({'registry': registry, 'request': request})
    root = app.root_factory(request)
    request.root = root

    # use same env variable as substanced catalog to determine
    # if we want to upgrade definitions
    autosync = asbool(
        os.environ.get(
        'SUBSTANCED_CATALOGS_AUTOSYNC',
        settings.get(
            'substanced.catalogs.autosync',
            settings.get('substanced.autosync_catalogs', False) # bc
            )))

    existing_definitions = root.get_services_definition()
    if autosync:
        for definition in existing_definitions.values():
            if hasattr(definition, '_broken_object'):
                root.delfromproperty('services_definition', definition)

    for definition in core.SERVICES_DEFINITION.values():
        old_def = existing_definitions.get(definition.service_id, None)
        if old_def is None:
            root.addtoproperty('services_definition', definition)

    core.SERVICES_DEFINITION.clear()

    # other init functions
    init_site_folders(root)
    init_contents(registry)
    init_sites_social_login(root)
    transaction.commit()
    manager.pop()


def init_contents(registry):
    """Init searchable content"""
    core.SEARCHABLE_CONTENTS = {
        type_id: c
        for type_id, c in registry.content.content_types.items()
        if core.SearchableEntity in c.mro()
    }


def init_site_folders(root):
    """init site folders"""
    for site in root.site_folders:
        site.init_files()


@subscriber(ObjectRemoved)
def remove_alerts(event):
    oids = event.removed_oids
    alerts = get_alerts_by_subject(oids)
    for alert in alerts:
        site = getattr(alert, '__parent__', None)
        if site and not alert.subjects:
            site.delfromproperty('alerts', alert)
