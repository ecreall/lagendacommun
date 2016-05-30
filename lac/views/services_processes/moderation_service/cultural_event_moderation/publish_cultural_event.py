# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config


from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.content.processes.services_processes.\
    moderation_service.cultural_event_moderation.behaviors import (
        PublishCulturalEvent)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _


class PublishCulturalEventViewStudyReport(BasicView):
    title = 'Alert for publishing'
    name = 'alertforpublishing'
    template = 'lac:views/services_processes/moderation_service/cultural_event_moderation/templates/alert_event_publishing.pt'

    def update(self):
        result = {}
        not_published_contents = [a for a in self.context.artists
                                  if 'published' not in a.state]
        not_published_contents.extend([s.venue for s in self.context.schedules
                                       if s.venue and 'published' not in s.venue.state])
        values = {'not_published_contents': not_published_contents}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class PublishCulturalEventView(FormView):
    title = _('Publish')
    name = 'publishculturaleventform'
    formid = 'formpublishculturalevent'
    behaviors = [PublishCulturalEvent, Cancel]
    validate_behaviors = False


@view_config(
    name='moderationpublishculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class PublishCulturalEventViewMultipleView(MultipleView):
    title = _('Publish the cultural event')
    name = 'moderationpublishculturalevent'
    viewid = 'moderationpublishculturalevent'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (PublishCulturalEventViewStudyReport, PublishCulturalEventView)
    validators = [PublishCulturalEvent.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {PublishCulturalEvent: PublishCulturalEventViewMultipleView})
