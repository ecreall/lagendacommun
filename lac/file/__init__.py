
from substanced.content import content
from substanced.util import get_oid

from dace.objectofcollaboration.entity import Entity
from dace.descriptors import CompositeMultipleProperty
from pontus.file import Image as PontusImage, OBJECT_OID

from lac.utilities.img_utility import (
    generate_images, AVAILABLE_FORMATS)
from lac import log


def get_file_data(picture, duplicate=False):
    result = {}
    if picture:
        result['picture'] = picture.get_data(None)
        if not duplicate:
            result['picture'][OBJECT_OID] = str(get_oid(picture))

    return result


@content(
    'lac_image',
    icon='glyphicon glyphicon-picture',
    )
class Image(PontusImage, Entity):

    variants = CompositeMultipleProperty('variants')

    def __init__(self, fp, mimetype=None, filename=None, **kwargs):
        super(Image, self).__init__(fp, mimetype, filename, **kwargs)

    def set_data(self, appstruct, omit=('_csrf_token_', '__objectoid__')):
        super(Image, self).set_data(appstruct, omit)
        try:
            self.generate_variants()
        except Exception as e:
            log.warning(e)

    def generate_variants(self):
        dimension = self.get_area_of_interest_dimension()
        results = generate_images(self.fp, self.filename, dimension)
        self.setproperty('variants', [])
        for img in results:
            img_val = PontusImage(img['fp'], self.mimetype,
                                  self.filename)
            img_val.__name__ = img['id']
            self.addtoproperty('variants', img_val)
            try:
                delattr(self, img_val.__name__)
            except AttributeError:
                pass

    def __getattr__(self, name):
        if name in AVAILABLE_FORMATS:
            attr = self.get(name)
            if attr is None:
                raise AttributeError(name)

            return attr
        else:
            return super(Image, self).__getattr__(name)
