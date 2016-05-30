# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.view import view_config

from substanced.util import get_oid

from dace.processinstance.core import DEFAULTMAPPING_ACTIONS_VIEWS
from pontus.default_behavior import Cancel
from pontus.form import FormView
from pontus.schema import select, omit
from pontus.file import OBJECT_OID

from lac.utilities.utils import get_site_folder
from lac.content.processes.admin_process.behaviors import (
    ConfigureSiteFolder)
from lac.content.site_folder import (
    SiteFolderSchema, SiteFolder)
from lac import _
from lac.mail import DEFAULT_SITE_MAILS


def add_file_data(container, attr):
    file_ = container.get(attr, None)
    if file_ and hasattr(file_, 'get_data'):
        container[attr] = file_.get_data(None)
        container[attr][OBJECT_OID] = str(get_oid(file_))

    return container


@view_config(
    name='configuresitefolder',
    context=SiteFolder,
    renderer='pontus:templates/views_templates/grid.pt',
    )
class ConfigureSiteFolderView(FormView):

    title = _('Configure the site folder')
    schema = select(SiteFolderSchema(factory=SiteFolder,
                                     editable=True,
                                     omit=('mail_templates', )),
                    ['filter_conf',
                     'mail_conf',
                     'ui_conf',
                     'pub_conf',
                     'keywords_conf',
                     'other_conf'
                     ])
    behaviors = [ConfigureSiteFolder, Cancel]
    formid = 'formconfiguresitefolder'
    name = 'configuresitefolder'

    def before_update(self):
        site = self.context
        services = site.get_all_services(
            kinds=['extractionservice'], delegation=False)
        has_extraction = 'extractionservice' in services
        if not has_extraction:
            self.schema = omit(self.schema, ['pub_conf'])
        else:
            has_periodic = getattr(
                services['extractionservice'][0], 'has_periodic', False)
            if not has_periodic:
                self.schema = omit(
                    self.schema,
                    [('pub_conf', ['closing_date',
                                   'closing_frequence',
                                   'delay_before_publication',
                                   'publication_number'])])

    def default_data(self):
        localizer = self.request.localizer
        data = self.context.get_data(self.schema)
        templates = [self.context.get_mail_template(mail_id)
                     for mail_id in DEFAULT_SITE_MAILS]
        for template in templates:
            template['title'] = localizer.translate(
                template['title'])

        ui_conf = data.get('ui_conf', {})
        if ui_conf:
            ui_conf = add_file_data(ui_conf, 'picture')
            ui_conf = add_file_data(ui_conf, 'favicon')
            ui_conf = add_file_data(ui_conf, 'theme')
            data['ui_conf'] = ui_conf

        pub_conf = data.get('pub_conf', {})
        if pub_conf:
            pub_conf = add_file_data(pub_conf, 'extraction_template')
            data['pub_conf'] = pub_conf

        templates = sorted(templates, key=lambda e: e['mail_id'])
        data['mail_conf'] = {'mail_templates': templates}
        data[OBJECT_OID] = str(get_oid(self.context))
        return data


DEFAULTMAPPING_ACTIONS_VIEWS.update({ConfigureSiteFolder: ConfigureSiteFolderView})
