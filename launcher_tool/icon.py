#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Windows ICO file load/save to .ico file and resource file (.exe, .dll).
"""
# based on https://en.wikipedia.org/wiki/ICO_(file_format)
# and https://blogs.msdn.microsoft.com/oldnewthing/20120720-00/?p=7083

import struct
import collections

TYPE_ICO = 1
ImageInfo = collections.namedtuple('ImageInfo',
                                   ['width', 'height', 'colors', 'reserved',
                                    'planes', 'bpp', 'size', 'offset'])

ICONDIR = '<HHH'
ICONDIRENTRY = '<BBBBHHII'

GRPICONDIR = '<HHH'  # idReserved idType idCount folowed by GRPICONDIRENTRY idEntries[]
GRPICONDIRENTRY = '<BBBBHHIH'  # bWidth bHeight bColorCount bReserved wPlanes wBitCount dwBytesInRes nId;
RT_ICON = 3
RT_GROUP_ICON = 14


class Icon(object):
    """Hanles Windows icons"""

    def __init__(self):
        self.images = []
        self.data = []

    def clear(self):
        """Erase current icon data"""
        self.images = []
        self.data = []

    def load(self, filename):
        """Load icon from file"""
        self.clear()
        with open(filename, 'rb') as ico_file:
            _, image_type, num_images = struct.unpack(ICONDIR, ico_file.read(6))
            if image_type != TYPE_ICO:
                raise TypeError('not an ICO file')
            for n in range(num_images):
                image_info = ImageInfo(*struct.unpack(ICONDIRENTRY, ico_file.read(16)))
                self.images.append(image_info)
            for image_info in self.images:
                ico_file.seek(image_info.offset)
                self.data.append(ico_file.read(image_info.size))

    def save(self, filename):
        """Save icon to file"""
        updated_image_info = []
        with open(filename, 'wb') as ico_file:
            ico_file.seek(struct.calcsize(ICONDIR) + struct.calcsize(ICONDIRENTRY) * len(self.images))
            for image_info, data in zip(self.images, self.data):
                pos = ico_file.tell()
                ico_file.write(data)
                updated_image_info.append(ImageInfo(
                    image_info.width,
                    image_info.height,
                    image_info.colors,
                    image_info.reserved,
                    image_info.planes,
                    image_info.bpp,
                    len(data),
                    pos))
            ico_file.seek(0)
            ico_file.write(struct.pack(ICONDIR, 0, TYPE_ICO, len(self.images)))
            for image_info in updated_image_info:
                ico_file.write(struct.pack(ICONDIRENTRY, *image_info))

    def load_from_resource(self, res, res_name, res_lang=1033):
        """Load icon from resource"""
        self.clear()
        info = res.get_resource(RT_GROUP_ICON, res_name, res_lang)
        _, image_type, num_images = struct.unpack(GRPICONDIR, info[0:6])
        offset = struct.calcsize(ICONDIR)
        for n in range(num_images):
            image_info = ImageInfo(*struct.unpack(GRPICONDIRENTRY, info[offset : offset + 16]))
            self.images.append(image_info)
            offset += struct.calcsize(ICONDIRENTRY)
        for image_info in self.images:
            self.data.append(res.get_resource(RT_ICON, image_info.offset, res_lang))

    def save_as_resource(self, res, res_name, res_lang=1033):
        """Store icon as resource"""
        info = [struct.pack(GRPICONDIR, 0, TYPE_ICO, len(self.images))]
        for n, (image_info, data) in enumerate(zip(self.images, self.data), 1):
            info.append(struct.pack(GRPICONDIRENTRY,
                                    image_info.width,
                                    image_info.height,
                                    image_info.colors,
                                    image_info.reserved,
                                    image_info.planes,
                                    image_info.bpp,
                                    len(data),
                                    n))
            res.update(RT_ICON, n, res_lang, data)
        res.update(RT_GROUP_ICON, res_name, res_lang, b''.join(info))
