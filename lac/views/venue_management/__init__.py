import colander

from pontus.widget import TextInputWidget

from lac.content.venue import (
    VenueSchema as OriginVenue)
from lac import _


class VenueSchema(OriginVenue):

    title = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_('Title')
        )
