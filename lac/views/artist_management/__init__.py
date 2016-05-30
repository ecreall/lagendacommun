# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander

from pontus.widget import TextInputWidget

from lac.content.artist import (
    ArtistInformationSheetSchema as originAS)
from lac import _


class ArtistInformationSheetSchema(originAS):

    title = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_('Title')
        )
