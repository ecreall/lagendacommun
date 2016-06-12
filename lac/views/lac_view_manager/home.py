# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import math
import datetime
import pytz
from pyramid.view import view_config
from pyramid.threadlocal import get_current_request
from substanced.objectmap import find_objectmap
from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from dace.objectofcollaboration.principal.util import get_current
from dace.util import find_catalog
from pontus.view import BasicView
from pontus.util import merge_dicts

from lac.content.processes.lac_view_manager.behaviors import (
    SeeHome)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac.content.interface import ISmartFolder
from lac.utilities.smart_folder_utility import get_folder_content
from lac.utilities.utils import get_site_folder
from lac.content.smart_folder import SmartFolder
from lac.content.site_configuration import (
    DEFAULT_DAYS_VISIBILITY)
from lac.views.filter import find_entities
from lac.views.user_management.login import LoginView


MORE_NB = 3


@view_config(
    name='index',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
@view_config(
    name='',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SeeHomeView(BasicView):
    title = ''
    name = ''
    behaviors = [SeeHome]
    template = 'lac:views/lac_view_manager/templates/home.pt'
    viewid = 'seehome'
    wrapper_template = 'daceui:templates/simple_view_wrapper.pt'
    container_css_class = 'home'

    def login(self):
        log_instance = LoginView(self.context, self.request)
        return log_instance()

    def update(self):
        if self.request.POST and 'login_form.submitted' in self.request.POST:
            log_result = self.login()
            if not isinstance(log_result, dict):
                return log_result

        self.execute(None)
        site = get_site_folder(True)
        self.title = site.title
        site_id = get_oid(site)
        user = get_current()
        folders = find_entities(
            interfaces=[ISmartFolder],
            metadata_filter={'states': ['published']},
            force_local_control=True)
        my_folders = []
        if self.request.user:
            my_folders = getattr(user, 'folders', [])
            my_folders = [folder for folder in my_folders
                          if isinstance(folder, SmartFolder) and
                          not folder.parents and
                          'private' in folder.state]

        folders = [folder for folder in folders
                   if not folder.parents and
                   getattr(folder, 'add_as_a_block', False)]
        folders.extend(my_folders)
        foldersdata = []
        old_date = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(
            days=getattr(site, 'days_visibility', DEFAULT_DAYS_VISIBILITY))
        old_date = old_date.replace(tzinfo=pytz.UTC)
        lac_catalog = find_catalog('lac')
        release_date_index = lac_catalog['release_date']
        query = release_date_index.ge(old_date)
        content_types = getattr(site, 'home_content_types',
                                ['review', 'cinema_review',
                                 'brief', 'interview'])
        for folder in folders:
            all_folders = [folder]
            all_folders.extend(folder.all_sub_folders('published'))
            contents_oids = set()
            for sub_folder in all_folders:
                result_set = get_folder_content(
                    sub_folder, user,
                    sort_on='release_date',
                    reverse=True,
                    limit=MORE_NB,
                    add_query=query,
                    metadata_filter={'content_types': content_types,
                                     'states': ['published']}
                    )
                contents_oids |= set(result_set.ids)

            if contents_oids:
                contents_oids = release_date_index.sort(
                    contents_oids, reverse=True, limit=MORE_NB)
                objectmap = find_objectmap(get_current_request().root)
                resolver = objectmap.object_for
                contents = [resolver(oid) for oid in contents_oids]
                foldersdata.append({'folder': folder,
                                    'contents': contents,
                                    'order': folder.get_order(site_id)})

        foldersdata = sorted(foldersdata, key=lambda e: e['order'])
        result = {}
        values = {'folders': foldersdata,
                  'content_types': content_types,
                  'row_len': math.ceil(len(foldersdata)/2)}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        result = merge_dicts(self.requirements_copy, result)
        return result


DEFAULTMAPPING_ACTIONS_VIEWS.update({SeeHome: SeeHomeView})
