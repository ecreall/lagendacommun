# -*- coding: utf8 -*-
# Copyright (c) 2014 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

import colander
from PIL import Image
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from substanced.util import get_oid

from pontus.view import BasicView
from dace.objectofcollaboration.entity import Entity
from dace.util import getSite, get_obj

from lac.ips.hexagonit.swfheader import parse
from lac import _
from lac.core import advertising_banner_config
from lac.views.filter import find_entities
from lac.content.interface import (
    IWebAdvertising)
from lac.content.keyword import ROOT_TREE
from lac import log


def validate_file_content(node, appstruct, width, height):
    if appstruct['picture']:
        mimetype = appstruct['picture']['mimetype']
        file_value = getattr(appstruct['picture']['fp'], 'raw',
                             appstruct['picture']['fp'])
        if mimetype.startswith('image'):
            try:
                file_value.seek(0)
            except Exception as e:
                log.warning(e)

            img = Image.open(file_value)
            img_width = img.size[0]
            img_height = img.size[1]
            file_value.seek(0)
            if img_width > width or img_height > height:
                raise colander.Invalid(node, _
                    (_('The image size is not valid: the allowed size is ${width} x ${height} px.',
                         mapping={'width': width,
                                   'height': height})))

        if mimetype.startswith('application/x-shockwave-flash'):
            try:
                file_value.seek(0)
            except Exception as e:
                log.warning(e)

            header = parse(file_value)
            file_value.seek(0)
            flash_width = header['width']
            flash_height = header['height']
            if flash_width > width or flash_height > height:
                raise colander.Invalid(node, _
                    (_('The flash animation size is not valid: the allowed size is ${width} x ${height} px.',
                         mapping={'width': width,
                                   'height': height})))


@view_config(
    name='banner_click',
    renderer='pontus:templates/views_templates/grid.pt',
    )
class BannerClick(BasicView):
    title = ''
    name = 'banner_click'
    viewid = 'banner_click'

    def update(self):
        ad_oid = self.params('ad_oid')
        try:
            ad_oid = int(ad_oid)
        except (ValueError, TypeError):  # invalid literal for int() with base 10
            ad_oid = None

        if not ad_oid:
            return HTTPFound(self.request.resource_url(self.request.root, ''))

        advertisting = get_obj(ad_oid)
        if advertisting:
            setattr(advertisting, 'click',
                    (getattr(advertisting, 'click', 0) + 1))
            url = getattr(advertisting, 'advertisting_url',
                   self.request.resource_url(self.request.root))
            return HTTPFound(url)

        return HTTPFound(self.request.resource_url(self.request.root, ''))


def default_validator(node, appstruct):
    return True


class AdvertistingBanner(object):

    title = _('Banner')
    description = _('Banner for advertistings')
    tags = ['advertisting']
    name = 'banner'
    order = -1
    validator = default_validator

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_context(self, root):
        """get real context for smart folder"""
        context = self.context
        is_root = False
        if context is root:
            is_root = True
            context = self.request.get_site_folder

        if self.request.view_name == 'open':
            params = dict(self.request.GET)
            if self.request.POST:
                params.update(dict(self.request.POST))

            if params:
                folderid = params.get('folderid', None)
                try:
                    if folderid:
                        is_root = False
                        return get_obj(int(folderid)), is_root
                except (TypeError, ValueError):
                    return context, is_root

        return context, is_root

    def find_advertistings(self):
        #TODO frequence
        root = getSite()
        context, is_root = self.get_context(root)
        keywords = []
        if hasattr(context, 'get_all_keywords'):
            keywords = list(context.get_all_keywords())
        else:
            keywords = list(getattr(context, 'keywords', []))

        if not keywords:
            keywords = [ROOT_TREE]

        advertisings = getattr(self.request, 'cache_advertisings', None)
        if advertisings is None:
            site = str(get_oid(self.request.get_site_folder))
            advertisings = find_entities(
                interfaces=[IWebAdvertising],
                keywords=keywords,
                metadata_filter={'states': ['published']},
                other_filter={'sources': [site]},
                force_publication_date=True)
            self.request.cache_advertisings = advertisings

        advertisings = [a for a in advertisings
                        if self.name in getattr(a, 'positions', [])]
        if not is_root:
            advertisings = sorted(
                advertisings,
                key=lambda e:
                    getattr(e, 'tree', {}).get(ROOT_TREE, {}) and 1 or 2)

        return advertisings

    def __call__(self):
        advertistings = self.find_advertistings()
        advertistings_data = [ad.get_content_data(self.request)
                              for ad in advertistings]
        return {'sources': advertistings_data}


def top_validator(node, appstruct):
    validate_file_content(node, appstruct, 728, 90)


@advertising_banner_config(
    name='advertisting_top',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_top.pt'
    )
class BannerTop(AdvertistingBanner):

    title = _('At the top')
    description = _('The top banner')
    name = 'advertisting_top'
    order = 0
    validator = top_validator


def right_validator(node, appstruct):
    validate_file_content(node, appstruct, 240, 90)


@advertising_banner_config(
    name='game_right_1',
    context=Entity,
    renderer='templates/panels/advertisting/game_right_1.pt'
    )
class BannerRight4(AdvertistingBanner):

    title = _('First on the right (games banner)')
    description = _('First on the right games banner')
    tags = ['game']
    name = 'game_right_1'
    order = 1
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_1',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_1.pt'
    )
class BannerRight1(AdvertistingBanner):

    title = _('First on the right')
    description = _('First on the right banner')
    name = 'advertisting_right_1'
    order = 2
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_2',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_2.pt'
    )
class BannerRight2(AdvertistingBanner):

    title = _('Second on the right')
    description = _('Second on the right banner')
    name = 'advertisting_right_2'
    order = 3
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_3',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_3.pt'
    )
class BannerRight3(AdvertistingBanner):

    title = _('Third on the right')
    description = _('Third on the right banner')
    name = 'advertisting_right_3'
    order = 4
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_5',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_5.pt'
    )
class BannerRight5(AdvertistingBanner):

    title = _('Fourth on the right')
    description = _('Fourth on the right banner')
    name = 'advertisting_right_5'
    order = 5
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_6',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_6.pt'
    )
class BannerRight6(AdvertistingBanner):

    title = _('Fifth on the right')
    description = _('Fifth on the right banner')
    name = 'advertisting_right_6'
    order = 6
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_7',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_7.pt'
    )
class BannerRight7(AdvertistingBanner):

    title = _('Sixth on the right')
    description = _('Sixth on the right banner')
    name = 'advertisting_right_7'
    order = 7
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_8',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_8.pt'
    )
class BannerRight8(AdvertistingBanner):

    title = _('Seventh on the right')
    description = _('Seventh on the right banner')
    name = 'advertisting_right_8'
    order = 8
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_9',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_9.pt'
    )
class BannerRight9(AdvertistingBanner):

    title = _('Eighth on the right')
    description = _('Eighth on the right banner')
    name = 'advertisting_right_9'
    order = 9
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_10',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_10.pt'
    )
class BannerRight10(AdvertistingBanner):

    title = _('Ninth on the right')
    description = _('Ninth on the right banner')
    name = 'advertisting_right_10'
    order = 10
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_right_11',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_right_11.pt'
    )
class BannerRight11(AdvertistingBanner):

    title = _('Tenth on the right')
    description = _('Tenth on the right banner')
    name = 'advertisting_right_11'
    order = 11
    # validator = right_validator


@advertising_banner_config(
    name='advertisting_middle',
    context=Entity,
    renderer='templates/panels/advertisting/advertisting_middle.pt'
    )
class BannerMiddle(AdvertistingBanner):

    title = _('In the middle')
    description = _('The middle banner')
    name = 'advertisting_middle'
    order = 5
    # validator = right_validator
