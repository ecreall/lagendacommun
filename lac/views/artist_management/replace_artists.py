# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from dace.util import get_obj
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import Schema, omit
from pontus.widget import AjaxSelect2Widget
from pontus.file import Object as ObjectType
from pontus.view import BasicView, ViewError

from lac.content.processes.artist_management.behaviors import (
    ReplaceArtistInformationSheet,
    ReplaceArtistInformationSheetMember)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _, log


def title_getter(id):
    try:
        obj = get_obj(int(id), None)
        if obj:
            return obj.title
        else:
            return id
    except Exception as e:
        log.warning(e)
        return id


@colander.deferred
def targets_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_artists'})
    values.append((0, ('', _('- Select -'))))
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="artists-container review-artists",
        multiple=True,
        title_getter=title_getter
        )


@colander.deferred
def target_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    values = []
    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_artists'})
    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="artists-container review-artists",
        title_getter=title_getter
        )


class ReplaceArtistsSchema(Schema):

    source = colander.SchemaNode(
        ObjectType(),
        widget=target_choice,
        title=_("Artist")
    )

    targets = colander.SchemaNode(
        colander.Set(),
        widget=targets_choice,
        title=_("Doubloons")
    )


@view_config(
    name='replaceartistinformationsheet',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ReplaceArtistInformationSheetView(FormView):

    title = _('Merge artist information sheets')
    schema = ReplaceArtistsSchema()
    behaviors = [ReplaceArtistInformationSheet, Cancel]
    formid = 'formreplaceartistinformationsheet'
    name = 'replaceartistinformationsheet'

    def default_data(self):
        return self.context.get_data(omit(self.schema,
                                          ['_csrf_token_', '__objectoid__']))


@view_config(
    name='mergeartist',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class MergeArtistView(BasicView):

    title = _('Merge artists')
    behaviors = [ReplaceArtistInformationSheetMember]
    name = 'mergeartist'

    def update(self):
        source_oid = self.params('source')
        targets_oid = self.params('targets')
        if targets_oid and source_oid:
            try:
                if not isinstance(targets_oid, (list, tuple)):
                    targets_oid = [targets_oid]

                targets = [get_obj(int(t)) for t in targets_oid]
                source = get_obj(int(source_oid))
                if targets and source:
                    result = self.execute(
                        {'source': source,
                         'targets': targets})
                    if result and result[0].get('error', False):
                        view_error = ViewError()
                        view_error.principalmessage = _("An error has occurred.")
                        return self.failure(view_error)

                    return HTTPFound(
                        self.request.resource_url(source, '@@index'))
            except Exception as error:
                log.warning(error)

        return HTTPFound(self.request.resource_url(self.context, ''))


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ReplaceArtistInformationSheet:
        ReplaceArtistInformationSheetView})


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {ReplaceArtistInformationSheetMember:
        MergeArtistView})
