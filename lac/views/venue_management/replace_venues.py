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
from pontus.schema import Schema
from pontus.widget import AjaxSelect2Widget
from pontus.file import Object as ObjectType
from pontus.view import BasicView, ViewError

from lac.content.processes.venue_management.behaviors import (
    ReplaceVenue,
    ReplaceVenueMember)
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
    venues = []
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_venues'})
    return AjaxSelect2Widget(
        values=venues,
        ajax_url=ajax_url,
        title_getter=title_getter,
        ajax_item_template="venue_item_template",
        css_class="venue-title",
        multiple=True)


@colander.deferred
def target_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    venues = []
    ajax_url = request.resource_url(context,
                                    '@@culturaleventmanagement',
                                    query={'op': 'find_venues'})
    return AjaxSelect2Widget(
        values=venues,
        ajax_url=ajax_url,
        title_getter=title_getter,
        ajax_item_template="venue_item_template",
        css_class="venue-title",
        multiple=False)


class ReplaceVenuesSchema(Schema):

    source = colander.SchemaNode(
        ObjectType(),
        widget=target_choice,
        title=_("Venue")
        )

    targets = colander.SchemaNode(
        colander.Set(),
        widget=targets_choice,
        title=_("Doubloons")
        )


@view_config(
    name='replacevenue',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ReplaceVenueView(FormView):

    title = _('Merge venues')
    schema = ReplaceVenuesSchema()
    behaviors = [ReplaceVenue, Cancel]
    formid = 'formreplacevenue'
    name = 'replacevenue'


@view_config(
    name='mergevenue',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class MergeVenueView(BasicView):

    title = _('Merge venues')
    behaviors = [ReplaceVenueMember]
    name = 'mergevenue'

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


DEFAULTMAPPING_ACTIONS_VIEWS.update({ReplaceVenue: ReplaceVenueView})

DEFAULTMAPPING_ACTIONS_VIEWS.update({ReplaceVenueMember: MergeVenueView})
