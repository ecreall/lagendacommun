# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform
from zope.interface import invariant

from dace.objectofcollaboration.principal.util import get_current
from dace.util import getSite, get_obj
from pontus.schema import Schema, select, omit
from pontus.core import VisualisableElementSchema
from pontus.widget import (
    TextInputWidget,
    AjaxSelect2Widget,
    ImageWidget,
    SimpleMappingWidget,
    SequenceWidget
    )
from pontus.file import ObjectData
from pontus.form import FileUploadTempStore
from deform_treepy.widget import (
    DictSchemaType)

from lac import _, log
from lac.content.artist import (
    ArtistInformationSheet, ArtistInformationSheetSchema)
from lac.core import SearchableEntitySchema
from lac.file import Image
from lac.content.interface import ISmartFolder
from lac.views.filter import find_entities
from lac.views.widget import (
    EmailInputWidget, PhoneWidget,
    PhoneValidator, ArticleRichTextWidget, RichTextWidget)


class ContactSchema(Schema):

    email = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        missing="",
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        )

    phone = colander.SchemaNode(
        DictSchemaType(),
        missing="",
        validator=colander.All(
            PhoneValidator()),
        widget=PhoneWidget(css_class="contact-phone"),
        title=_('Phone'),
        description=_("Indicate the phone number. Only spaces are allowed as separator for phone numbers.")
        )

    surtax = colander.SchemaNode(
        colander.String(),
        missing="0",
        widget=TextInputWidget(item_css_class="hide-bloc"),
        default="0",
        title=_('Surtax'),
        description=_('Indicate the amount of the surcharge (for the premium-rate number).'),
        )

    fax = colander.SchemaNode(
        DictSchemaType(),
        validator=colander.All(
            PhoneValidator(
                _('${phone} fax number not valid for the selected country (${country})'))),
        missing="",
        widget=PhoneWidget(css_class="contact-fax"),
        title=_('Fax'),
        description=_("Indicate the fax number. Only spaces are allowed as separator for fax numbers.")
        )

    website = colander.SchemaNode(
        colander.String(),
        missing="",
        title=_('Website'),
        )

    @invariant
    def contact_invariant(self, appstruct):
        appstruct_copy = appstruct.copy()
        appstruct_copy.pop('surtax')
        if 'title' in appstruct_copy:
            appstruct_copy.pop('title')

        if not any(v != "" and v != colander.null
                   for v in list(appstruct_copy.values())):
            raise colander.Invalid(self,
                                   _('One value must be entered.'))

        if 'phone' in appstruct and appstruct['phone'] and \
            ('surtax' not in appstruct or \
             'surtax' in appstruct and not appstruct['surtax']):
            raise colander.Invalid(self,
                                   _('Surtax field must be filled in.'))


@colander.deferred
def picture_widget(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    tmpstore = FileUploadTempStore(request)
    source = None
    if context is not root:
        if context.picture:
            source = context.picture

    return ImageWidget(
        tmpstore=tmpstore,
        max_height=500,
        max_width=400,
        source=source,
        selection_message=_("Upload image.")
        )


@colander.deferred
def article_widget(node, kw):
    request = node.bindings['request']
    css_links = []
    js_links = []
    css_links.append(request.static_url(
                            'lac:static/css'
                            '/bootstrap.css'))
    css_links.append(request.static_url(
                            'lac:static/css'
                            '/article.css'))
    css_links.append(request.static_url(
                            'deform:static/tinymce/skins'
                            '/lightgray/skin.min.css'))
    nodes = find_entities(
        interfaces=[ISmartFolder],
        metadata_filter={'states': ['published']},
        force_local_control=True)
    nodes = [{'title': sf.title, 'style': 'color:'+sf.style['usual_color'].split(',')[1]}
             for sf in nodes if not sf.parents]
    return ArticleRichTextWidget(
        css_links=css_links,
        js_links=js_links,
        styles_folders=nodes)


@colander.deferred
def artists_choice(node, kw):
    context = node.bindings['context']
    request = node.bindings['request']
    root = getSite()
    values = []
    if context is not root:
        values = [(a.get_id(), a.title) for a in context.artists]

    ajax_url = request.resource_url(context,
                                    '@@creationculturelapi',
                                    query={'op': 'find_artists'})

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

    return AjaxSelect2Widget(
        values=values,
        ajax_url=ajax_url,
        css_class="artists-container review-artists",
        multiple=True,
        create=True,
        title_getter=title_getter,
        ajax_item_template="artist_item_template",
        ajax_selection_template='formatArtist'
        )


@colander.deferred
def default_signature(node, kw):
    user = get_current()
    return getattr(user, 'signature', '')


class BaseReviewSchema(VisualisableElementSchema, SearchableEntitySchema):
    """Schema for base review"""

    title = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_('Title')
        )

    surtitle = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_("Surtitle"),
        missing=""
        )

    article = colander.SchemaNode(
        colander.String(),
        widget=article_widget,
        title=_("Article")
        )

    description = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_("Description")
        )

    picture = colander.SchemaNode(
        ObjectData(Image),
        widget=picture_widget,
        title=_('Picture'),
        )

    artists_ids = colander.SchemaNode(
        colander.Set(),
        widget=artists_choice,
        title=_('Artists'),
        missing=[]
        )

    artists = colander.SchemaNode(
        colander.Sequence(),
        omit(select(ArtistInformationSheetSchema(editable=True, 
                                                 factory=ArtistInformationSheet,
                                                 omit=('id', ),
                            widget=SimpleMappingWidget(
                                  css_class='artist-data object-well'
                                            ' default-well'),
                                  name=_('artist')),
                    ['id', 'origin_oid', 'title',
                    'description', 'picture', 'biography', 'is_director']),
            ['_csrf_token_', '__objectoid__']),
        widget=SequenceWidget(css_class='artists-values',
                            template='lac:views/'
                                     'templates/sequence_modal.pt',
                            item_template='lac:views/'
                                          'templates/sequence_modal_item.pt'),
        title=_('Artists'),
        )

    signature = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(),
        title=_("Signature"),
        default=default_signature
        )

    informations = colander.SchemaNode(
        colander.String(),
        widget=RichTextWidget(),
        missing="",
        title=_("Informations")
        )

    showcase_review = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Add to the carousel of the home page'),
        title='',
        default=False,
        missing=False
        )
