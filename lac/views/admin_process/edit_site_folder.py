# -*- coding: utf8 -*-
# Copyright (c) 2015 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select

from lac.content.processes.admin_process.behaviors import (
    EditSiteFolder)
from lac.content.site_folder import (
    SiteFolderSchema, SiteFolder)
from lac import _



@view_config(
    name='editsitefolder',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class EditSiteFolderView(FormView):

    title = _('Edit the site folder')
    schema = select(SiteFolderSchema(factory=SiteFolder,
                                     editable=True),
                    ['title',
                     'urls_ids',
                     'description',
                     'contacts'
                     ])
    behaviors = [EditSiteFolder, Cancel]
    formid = 'formeditsitefolder'
    name = 'editsitefolder'
    requirements = {'css_links': [],
                    'js_links': ['lac:static/js/cultural_event_management.js',
                                 'lac:static/js/contact_management.js']}

    def default_data(self):
        return self.context


DEFAULTMAPPING_ACTIONS_VIEWS.update({EditSiteFolder: EditSiteFolderView})
