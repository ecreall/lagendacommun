# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import datetime
import colander
from pyramid.view import view_config

from dace.processinstance.core import (
    DEFAULTMAPPING_ACTIONS_VIEWS, Validator, ValidationError)
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import Schema, omit, select
from pontus.widget import SequenceWidget, SimpleMappingWidget
from pontus.view import BasicView
from pontus.view_operation import MultipleView

from lac.utilities.utils import get_site_folder
from lac.views.film_schedule_management import CinemaVenueSchema
from lac.content.processes.film_schedule_management.behaviors import (
    AddCinemagoer, ExtractSchedules)
from lac.content.lac_application import (
    CreationCulturelleApplication)
from lac import _
from lac.utilities.cinema_utility import (
    get_cinema_venues_data, next_weekday)


class CinemagoerViewStudyReport(BasicView):
    title = 'Clear'
    name = 'clear_cinemagoer'
    template = 'lac:views/film_schedule_management/templates/clear_btn.pt'

    def update(self):
        result = {}
        values = {'context': self.context}
        body = self.content(args=values, template=self.template)['body']
        item = self.adapt_item(body, self.viewid)
        result['coordinates'] = {self.coordinates: [item]}
        return result


class CinemagoerSchema(Schema):

    next_date = colander.SchemaNode(
        colander.Date(),
        title=_('End date of publication'),
        missing=None,
    )

    venues = colander.SchemaNode(
        colander.Sequence(),
        omit(select(CinemaVenueSchema(
            name='venue',
            title=_('Venue'),
            widget=SimpleMappingWidget(
                css_class="venue-block cinema-block object-well default-well")),
                    ['id', 'title', 'schedules']),
            ['_csrf_token_']),
        widget=SequenceWidget(min_len=1, css_class="add-venues-mode"),
        title=_('Cinemas'),
    )


class AddCinemagoerValidator(Validator):

    @classmethod
    def validate(cls, context, request, **kw):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        if services:
            raise ValidationError()

        return True


class AddCinemagoerExtractionValidator(Validator):

    @classmethod
    def validate(cls, context, request, **kw):
        site = get_site_folder(True)
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        if not services:
            raise ValidationError()

        return True


class AddCinemagoerView(FormView):

    title = _('Add cinema sessions')
    schema = CinemagoerSchema()
    behaviors = [AddCinemagoer, Cancel]
    validators = [AddCinemagoerValidator]
    formid = 'formaddcinemagoer'
    name = 'addcinemagoerform'

    def default_data(self):
        data = {'next_date': next_weekday(datetime.datetime.now(), 2),
                'venues': sorted(list(get_cinema_venues_data().values()),
                                 key=lambda e: e['title'].title)}
        return data


class AddCinemagoerExtractionView(AddCinemagoerView):
    behaviors = [AddCinemagoer, ExtractSchedules, Cancel]
    validators = [AddCinemagoerExtractionValidator]


@view_config(
    name='addcinemagoer',
    context=CreationCulturelleApplication,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class AddCinemagoerMultipleView(MultipleView):
    title = _('Add cinema sessions')
    name = 'addcinemagoer'
    viewid = 'addcinemagoer'
    template = 'daceui:templates/mergedmultipleview.pt'
    views = (CinemagoerViewStudyReport,
             AddCinemagoerView,
             AddCinemagoerExtractionView)
    validators = [AddCinemagoer.get_validator()]
    requirements = {
        'css_links': [],
        'js_links': ['lac:static/js/addresse_management.js',
                     'lac:static/js/cultural_event_management.js',
                     'lac:static/js/contact_management.js',
                     'lac:static/js/artist_management.js',
                     'lac:static/js/contextual_help_cinema_sessions.js',
                     'lac:static/js/cinemagoer.js']}

DEFAULTMAPPING_ACTIONS_VIEWS.update({AddCinemagoer: AddCinemagoerMultipleView})
