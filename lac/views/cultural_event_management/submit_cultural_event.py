# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms 
# available on http://www.gnu.org/licenses/agpl.html 

# licence: AGPL
# author: Amen Souissi

import colander
# import datetime
# import pytz
from pyramid.view import view_config
from pyramid import renderers

from dace.util import getSite
from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.view import BasicView
from pontus.view_operation import MultipleView
from pontus.file import Object as ObjectType
from pontus.widget import CheckboxChoiceWidget
from pontus.schema import Schema

from lac.content.processes.cultural_event_management.behaviors import (
    SubmitCulturalEvent,
    can_publish_in_periodic)
from lac.content.cultural_event import (
    CulturalEvent)
from lac import _
from lac.views.filter import visible_in_site


site_choice_template = 'lac:views/cultural_event_management/templates/site_choice.pt'


def render_site_data(site, context, request):
    services = site.get_all_services(
        kinds=['moderation', 'extractionservice'],
        delegation=False)
    moderations_data = []
    if 'moderation' in services:
        moderations = services['moderation']
        for moderation in moderations:
            price = moderation.price_str
            if price != 'Free':
                moderations_data.append((moderation.delegate.title, price))

    can_publish, site_publication_date,\
    end_date, has_extraction = can_publish_in_periodic(site, context)
    values = {'site': site,
              'moderations_data': moderations_data,
              'has_extraction': has_extraction,
              'can_publish': can_publish,
              'publication_date': site_publication_date,
              'end_date': end_date,
              'is_cultural_event': isinstance(context, CulturalEvent)}
    body = renderers.render(site_choice_template, values, request)
    return body


class SubmitCulturalEventViewStudyReport(BasicView):
    title = 'Alert for submission'
    name = 'alertforsubmission'
    template = 'lac:views/cultural_event_management/templates/alert_event_submission.pt'

    def update(self):
        result = {}
        #TODO
        current_site = self.request.get_site_folder
        sites = [current_site]
        sites.extend(current_site.get_group())
        sites = [s for s in sites
                 if visible_in_site(s, self.context, request=self.request)]
        sites_data = [(f, render_site_data(f, self.context, self.request)) for f
                      in sites]
        #TODO
        not_published_contents = [a for a in self.context.artists
                                  if 'published' not in a.state]
        not_published_contents.extend([s.venue for s in self.context.schedules
                                       if s.venue and 'published' not in s.venue.state])
        values = {'not_published_contents': not_published_contents,
                  'sites_data': sites_data}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


@colander.deferred
def sites_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    values = [(f, render_site_data(f, context, request)) for f
              in root.site_folders]
    return CheckboxChoiceWidget(values=values, multiple=True)


@colander.deferred
def sites_default(node, kw):
    return node.bindings['request'].get_site_folder


class SubmissionSchema(Schema):

    sites = colander.SchemaNode(
        ObjectType(),
        widget=sites_choice,
        default=sites_default,
        title=_('Sites'),
        validator=colander.Length(min=1)
        )


class SubmitCulturalEventView(FormView):
    title = _('Submit')
    name = 'submitculturaleventform'
    formid = 'formsubmitculturalevent'
    #schema = SubmissionSchema()
    behaviors = [SubmitCulturalEvent, Cancel]
    validate_behaviors = False


@view_config(
    name='submitculturalevent',
    context=CulturalEvent,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class SubmitCulturalEventViewMultipleView(MultipleView):
    title = _('Submit the cultural event')
    name = 'submitculturalevent'
    viewid = 'submitculturalevent'
    # template = 'daceui:templates/mergedmultipleview.pt'
    template = 'daceui:templates/simple_mergedmultipleview.pt'
    views = (SubmitCulturalEventViewStudyReport, SubmitCulturalEventView)
    validators = [SubmitCulturalEvent.get_validator()]


DEFAULTMAPPING_ACTIONS_VIEWS.update(
    {SubmitCulturalEvent: SubmitCulturalEventViewMultipleView})
