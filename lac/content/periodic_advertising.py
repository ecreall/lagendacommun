# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer
from pyramid.threadlocal import get_current_request

from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from pontus.widget import (
    Select2Widget)
from pontus.file import ObjectData, File

from .interface import IPeriodicAdvertising
from lac import _
from lac.core import (
    Advertising,
    AdvertisingSchema)
from lac.core import get_file_widget


ADVERTISING_POSITIONS = [
       ('double_central', _('Double central')),
       ('front_cover', _('Front cover')),
       ('back_cover', _('Back cover')),
       ('the_cartridge', _('The cartridge')),
       ('page_2', _('Page 2')),
       ('page_3', _('Page 3')),
       ('the_brief_side', _('The brief side'))
    ]


ADVERTISING_FORMAT = [
        ('full_page', _('Full page')),
        ('horizontal_half_page', _('Horizontal half page')),
        ('vertical_half_page', _('Vertical half page')),
        ('horizontal_quarter_page', _('Horizontal quarter page')),
        ('vertical_quarter_page', _('Vertical quarter page')),
        ('eighth_page', _('Eighth page')),
        ('sixteenth_page', _('Sixteenth page'))
    ]


def context_is_a_periodicadvertising(context, request):
    return request.registry.content.istype(context, 'periodicadvertising')


@colander.deferred
def format_widget(node, kw):
    values = ADVERTISING_FORMAT.copy()
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(
        css_class="periodic-setting periodic-format",
        values=values)


@colander.deferred
def positions_widget(node, kw):
    values = ADVERTISING_POSITIONS.copy()
    values.insert(0, ('', _('- Select -')))
    return Select2Widget(
        css_class="periodic-setting periodic-position",
        values=values)


class PeriodicAdvertisingSchema(AdvertisingSchema):
    """Schema for periodic advertising"""

    name = NameSchemaNode(
        editing=context_is_a_periodicadvertising,
        )

    picture = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['pdf', 'qxd', 'qxp']),
        title=_('Advertisement file'),
        description=_("Only PDF and Xpress files are supported."),
        )

    format = colander.SchemaNode(
        colander.String(),
        widget=format_widget,
        title=_('Format')
        )

    position = colander.SchemaNode(
        colander.String(),
        widget=positions_widget,
        title=_('Position')
        )


@content(
    'periodicadvertising',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IPeriodicAdvertising)
class PeriodicAdvertising(Advertising):
    """PeriodicAdvertising class"""

    type_title = _('Periodical advertisement')
    icon = 'lac-icon icon-periodic-advertising'
    templates = {'default': 'lac:views/templates/periodic_advertisting_result.pt',
                 'bloc': 'lac:views/templates/periodic_advertisting_result.pt'}
    name = renamer()

    def get_content_data(self, request=None):
        if request is None:
            request = get_current_request()

        result = {'url': '',
                  'type': 'none'}
        if self.picture:
            result = {'url': self.picture.url,
                      'filename': self.picture.filename}
            if self.picture.mimetype.startswith('application/pdf'):
                result['type'] = 'pdf'
            else:
                #application/quarkxpress, application/x-quark-express
                result['type'] = 'xpress'

        return result
