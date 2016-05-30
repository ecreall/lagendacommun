# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
import deform

from pyramid import renderers

from dace.util import getSite
from pontus.schema import omit, select, Schema
from pontus.widget import (
    SimpleMappingWidget,
    SequenceWidget,
    Select2Widget,
    CheckboxChoiceWidget,
    )
from pontus.file import ObjectData, File
from deform_treepy.widget import (
    DictSchemaType, KeywordsTreeWidget)
from deform_treepy.utilities.tree_utility import (
    tree_min_len)

from lac import _
from lac.mail import DEFAULT_SITE_MAILS
from lac.content.smart_folder import FilterSchema
from lac.content.keyword import KeywordsMappingSchema
from lac.core import (
    DEFAULT_TREE,
    DEFAULT_TREE_LEN,
    SITE_WIDGETS)
from lac.views.widget import (
    EmailInputWidget)
from lac.core import get_file_widget


DEFAULT_DAYS_VISIBILITY = 15


DEFAULT_DELAY_BEFORE_PUBLICATION = 8


DEFAULT_CLOSING_FREQUENCE = 7


class PublicationConfigurationSchema(Schema):

    """Schema for site configuration."""

    closing_date = colander.SchemaNode(
        colander.DateTime(),
        title=_('Closing date')
        )

    closing_frequence = colander.SchemaNode(
        colander.Integer(),
        default=DEFAULT_CLOSING_FREQUENCE,
        title=_('Closing frequence'),
        )

    delay_before_publication = colander.SchemaNode(
        colander.Integer(),
        default=DEFAULT_DELAY_BEFORE_PUBLICATION,
        title=_('Delay before publication'),
        )

    publication_number = colander.SchemaNode(
        colander.Integer(),
        default=0,
        title=_('Publication number'),
        )

    extraction_template = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['odt']),
        title=_('Extraction template'),
        missing=None,
        description=_("Only ODT files are supported."),
        )


@colander.deferred
def content_types_choices(node, kw):
    from lac import core
    request = node.bindings['request']
    values = []
    exclude_internal = request.user is None
    values = [(key, getattr(c, 'type_title', c.__class__.__name__))
              for key, c in list(core.SEARCHABLE_CONTENTS.items())
              if not exclude_internal or
              (exclude_internal and not getattr(c, 'internal_type', False))]

    values = sorted(values, key=lambda e: e[0])
    return Select2Widget(values=values, multiple=True)


@colander.deferred
def widgets_choices(node, kw):
    request = node.bindings['request']
    values = [(key, renderers.render(c['renderer'], c, request))
              for key, c in list(SITE_WIDGETS.items())]
    return CheckboxChoiceWidget(
        values=values)


class UserInterfaceConfigurationSchema(Schema):

    picture = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['png', 'jpg', 'svg']),
        title=_('Logo'),
        missing=None,
        description=_("Only PNG and SVG files are supported."),
        )

    favicon = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['ico']),
        title=_('Favicon'),
        missing=None,
        description=_("Only ICO file is supported."),
        )

    theme = colander.SchemaNode(
        ObjectData(File),
        widget=get_file_widget(file_extensions=['css']),
        title=_('Theme'),
        missing=None,
        description=_("Only CSS files are supported."),
        )

    widgets = colander.SchemaNode(
        colander.Set(),
        widget=widgets_choices,
        title=_('Widgets to display'),
        description=_('You can select widgets to be displayed.'),
        default=[]
    )

    days_visibility = colander.SchemaNode(
        colander.Integer(),
        default=DEFAULT_DAYS_VISIBILITY,
        title=_('Days visibility'),
        )

    home_content_types = colander.SchemaNode(
        colander.Set(),
        widget=content_types_choices,
        title=_('Content types to display'),
        description=_('You can select the content types to be displayed in homepage blocks.'),
        default=['review', 'cinema_review', 'brief', 'interview']
    )

    # @invariant
    # def banner_invariant(self, appstruct):
    #     if appstruct.get('picture', None):
    #         validate_file_content(self.get('picture'), appstruct, 1000, 33)


class MailTemplate(Schema):

    mail_id = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        title=_('Mail id'),
        )

    title = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        title=_('Title'),
        missing=""
        )

    subject = colander.SchemaNode(
        colander.String(),
        title=_('Subject'),
        )

    template = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_("Template")
        )


@colander.deferred
def templates_widget(node, kw):
    len_templates = len(DEFAULT_SITE_MAILS)
    return SequenceWidget(min_len=len_templates, max_len=len_templates)


@colander.deferred
def templates_default(node, kw):
    request = node.bindings['request']
    localizer = request.localizer
    values = []
    for temp_id in DEFAULT_SITE_MAILS:
        template = DEFAULT_SITE_MAILS[temp_id].copy()
        template['mail_id'] = temp_id
        template['title'] = localizer.translate(template['title'])
        values.append(template)

    values = sorted(values, key=lambda e: e['mail_id'])
    return values


class MailTemplatesConfigurationSchema(Schema):

    mail_templates = colander.SchemaNode(
        colander.Sequence(),
        omit(select(MailTemplate(name='template',
                                 title=_('Mail template'),
                                 widget=SimpleMappingWidget(
                                         css_class="object-well default-well mail-template-well mail-template-block")),
                        ['mail_id', 'title', 'subject', 'template']),
                    ['_csrf_token_']),
        widget=templates_widget,
        default=templates_default,
        missing=templates_default,
        title=_('Mail templates'),
        )


class FilterConfigurationSchema(Schema):

    filters = colander.SchemaNode(
        colander.Sequence(),
        omit(select(FilterSchema(name='filter',
                                 title=_('Filter'),
                                 widget=SimpleMappingWidget(
                                         css_class="object-well default-well mail-template-well mail-template-block")),
                       ['metadata_filter', 'geographic_filter',
                        'temporal_filter', 'contribution_filter',
                        'text_filter', 'other_filter']),
                 ["_csrf_token_"]),
        title=_('Filters'),
        widget=SequenceWidget(
            min_len=1,
            add_subitem_text_template=_('Add a new filter')))

    hold_filter = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Keep the filter after sign in'),
        title='',
        default=True,
        missing=True
        )


@colander.deferred
def keyword_widget(node, kw):
    root = getSite()
    can_create = 0
    levels = root.get_tree_nodes_by_level()
    return KeywordsTreeWidget(
        min_len=1,
        max_len=DEFAULT_TREE_LEN,
        can_create=can_create,
        levels=levels)


@colander.deferred
def keywords_validator(node, kw):
    if DEFAULT_TREE == kw or tree_min_len(kw) < 2:
        raise colander.Invalid(
            node, _('Minimum one categorie required.'))


class KeywordsConfSchema(Schema):

    tree = colander.SchemaNode(
        typ=DictSchemaType(),
        validator=colander.All(keywords_validator),
        widget=keyword_widget,
        default=DEFAULT_TREE,
        title=_('Categories'),
        )

    keywords_mapping = omit(KeywordsMappingSchema(widget=SimpleMappingWidget()),
                            ["_csrf_token_"])


@colander.deferred
def default_sender(node, kw):
    request = node.bindings['request']
    return request.registry.settings['lac.admin_email']


class OtherSchema(Schema):

    site_sender = colander.SchemaNode(
        colander.String(),
        widget=EmailInputWidget(),
        validator=colander.All(
            colander.Email(),
            colander.Length(max=100)
            ),
        default=default_sender,
        title=_('Site sender')
        )

    analytics = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextAreaWidget(rows=4, cols=60),
        title=_('Analytics'),
        missing=''
        )

    activate_questionnaire = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Activate the questionnaire'),
        title='',
        default=False,
        missing=False
    )

    activate_improve = colander.SchemaNode(
        colander.Boolean(),
        widget=deform.widget.CheckboxWidget(),
        label=_('Activate the improvement'),
        title='',
        default=False,
        missing=False
    )
