# -*- coding: utf-8 -*-
"""Tests for img cropper
"""

from lac.testing import FunctionalTests
from lac.utilities.img_utility import _get_coordinates


class TestCropper(FunctionalTests): #pylint: disable=R0904
    """Test Filters"""

    def setUp(self):
        super(TestCropper, self).setUp()

    def test_get_coordinates(self):
        height = 600
        width = 900
        area_height = 200
        area_width = 400
        x = 100
        y = 100
        h = 200
        l = 300
        result = _get_coordinates(height, width, area_height, area_width, x, y, h, l)
        self.assertTrue(result == (0, 0, 900, 600))
        h = 85
        l = 128
        result = _get_coordinates(height, width, area_height, area_width, x, y, h, l)
        self.assertTrue(result == (0, 0, 900, 598))
        h = 120
        l = 120
        result = _get_coordinates(height, width, area_height, area_width, x, y, h, l)
        self.assertTrue(result == (0, 0, 600, 600))
