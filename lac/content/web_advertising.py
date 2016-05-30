# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from zope.interface import implementer, invariant
from pyramid.threadlocal import get_current_request


from substanced.content import content
from substanced.schema import NameSchemaNode
from substanced.util import renamer

from pontus.widget import (
    Select2Widget,
    RichTextWidget)
from pontus.file import ObjectData, File
from deform_treepy.widget import (
    DictSchemaType, KeywordsTreeWidget)

from .interface import IWebAdvertising
from lac import _
from lac.core import (
    Advertising,
    AdvertisingSchema,
    ADVERTISING_CONTAINERS)
from lac.content.keyword import DEFAULT_TREE
from lac.core import get_file_widget


def context_is_a_webadvertising(context, request):
    return request.registry.content.istype(context, 'webadvertising')


@colander.deferred
def keyword_widget(node, kw):
    request = node.bindings['request']
    levels = request.get_site_folder.get_tree_nodes_by_level()
    level = len(levels)
    return KeywordsTreeWidget(
        min_len=1,
        max_len=level,
        can_create=level+1,
        levels=levels)


@colander.deferred
def advertisting_widget(node, kw):
    values = [(ad_id, value['title'])
              for ad_id, value in ADVERTISING_CONTAINERS.items()
              if 'advertisting' in value['tags']]
    values = sorted(values,
                    key=lambda e: ADVERTISING_CONTAINERS[e[0]]['order'])
    return Select2Widget(
        css_class="advertising-positions",
        values=values,
        multiple=True)


class WebAdvertisingSchema(AdvertisingSchema):
    """Schema for Web advertising"""

    name = NameSchemaNode(
        editing=context_is_a_webadvertising,
        )

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        missing=None,
        title=_('Categories'),
        )

    home_page = colander.SchemaNode(
        colander.Boolean(),
        default=False,
        missing=False,
        label=_('Not'),
        title=None,
        description=_('Home page'),
        )

    picture = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(item_css_class="advertising-file-content",
                          css_class="file-content",
                          file_type=['image', 'flash']),
        title=_('Advertisement file'),
        description=_("Only image and flash files are supported."),
        missing=None
        )

    html_content = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(item_css_class="advertising-html-content",
                              css_class="html-content-text"),
        title=_("Or HTML content"),
        missing=""
        )

    advertisting_url = colander.SchemaNode(
        colander.String(),
        title=_('URL'),
        missing="#"
        )

    positions = colander.SchemaNode(
        colander.Set(),
        widget=advertisting_widget,
        title=_('Positions')
        )

    @invariant
    def content_invariant(self, appstruct):
        if not(appstruct['html_content'] or appstruct['picture']):
            raise colander.Invalid(self, _
                        ('Content will be defined.'))

    @invariant
    def banner_invariant(self, appstruct):
        positions = appstruct['positions']
        if positions:
            for position in positions:
                ADVERTISING_CONTAINERS[position]['validator'](
                    self.get('picture'),
                    appstruct)


@content(
    'webadvertising',
    icon='glyphicon glyphicon-align-left',
    )
@implementer(IWebAdvertising)
class WebAdvertising(Advertising):
    """WebAdvertising class"""

    type_title = _('Web advertisement')
    icon = 'glyphicon glyphicon-picture'
    templates = {'default': 'lac:views/templates/web_advertisting_result.pt',
                 'bloc': 'lac:views/templates/web_advertisting_result.pt'}
    name = renamer()

    def __init__(self, **kwargs):
        self.click = 0
        super(WebAdvertising, self).__init__(**kwargs)

    def _extract_content(self):
        if self.picture:
            if self.picture.mimetype.startswith('image'):
                return {'content': self.picture.url,
                        'type': 'img'}

            if self.picture.mimetype.startswith(
                           'application/x-shockwave-flash'):
                return {'content': self.picture.url,
                        'type': 'flash'}

            if self.picture.mimetype.startswith('text/html'):
                blob = self.picture.blob.open()
                blob.seek(0)
                content = blob.read().decode("utf-8")
                blob.seek(0)
                blob.close()
                return {'content': content,
                        'type': 'html'}

        html_content = getattr(self, 'html_content', '')
        if html_content:
            return {'content': html_content,
                    'type': 'html'}

        return {'content': '',
                'type': 'none'}

    def get_positions(self):
        return [ADVERTISING_CONTAINERS[p]['title']
                for p in self.positions]

    def get_content_data(self, request=None):
        if request is None:
            request = get_current_request()

        root = request.root
        data = {'url': request.resource_url(
                root,
                'banner_click',
                query={'ad_oid': getattr(self, '__oid__', 0)}),
                }

        data.update(self._extract_content())
        return data
