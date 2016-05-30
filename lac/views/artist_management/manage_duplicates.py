# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi
import math
from pyramid.view import view_config

from substanced.util import get_oid

import html_diff_wrapper
from dace.objectofcollaboration.principal.util import (
    has_any_roles,
    get_current)
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.artist_management.behaviors import (
    ManageDuplicates)
from lac.utilities.duplicates_utility import (
    find_duplicates_artist)
from lac.content.artist import ArtistInformationSheet
from lac import _
from lac.utilities.utils import get_site_folder
from lac.content.processes.services_processes.moderation_service import (
    is_site_moderator)


class DoubloonArtistViewStudyReport(BasicView):
    title = 'Alert for remove'
    name = 'alertforremove'
    template = 'lac:views/artist_management/templates/alert_doubloon.pt'
    duplicates_state = ('published',)

    def get_adapted_target(self, oids, obj_oid, oid):
        if obj_oid in oids:
            oids.remove(obj_oid)

        oids.append(oid)
        return oids

    def update(self):
        result = {}
        site = get_site_folder(True, self.request)
        user = get_current(self.request)
        is_manager = has_any_roles(
            user=user,
            roles=('Admin', ('SiteAdmin', site))) or\
            is_site_moderator(self.request)
        duplicates = find_duplicates_artist(self.context, self.duplicates_state)
        diff_bodies = {}
        context_view = self.content(
            args={'object': self.context},
            template=self.context.templates.get('diff', None))['body']

        for duplicate in duplicates:
            duplicate_view = self.content(
                args={'object': duplicate},
                template=duplicate.templates.get('diff', None))['body']
            soupt, textdiff = html_diff_wrapper.render_html_diff(
                context_view, duplicate_view)
            diff_bodies[duplicate] = (textdiff, get_oid(duplicate))

        values = {'context': self.context,
                  'oid': get_oid(self.context),
                  'context_view': context_view,
                  'contents': diff_bodies,
                  'row_len': math.ceil(len(diff_bodies)/2),
                  'is_manager': is_manager,
                  'view': self}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class DoubloonArtistView(FormView):
    title = _('Remove')
    name = 'removeartistform'
    formid = 'formremoveartist'
    behaviors = [ManageDuplicates]
    validate_behaviors = False


@view_config(
    name='potentialduplicatesartist',
    context=ArtistInformationSheet,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class DoubloonArtistViewMultipleView(MultipleView):
    title = _('Duplicate detection')
    name = 'potentialduplicatesartist'
    viewid = 'potentialduplicatesartist'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (DoubloonArtistViewStudyReport, DoubloonArtistView)
    validators = [ManageDuplicates.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ManageDuplicates: DoubloonArtistViewMultipleView})
