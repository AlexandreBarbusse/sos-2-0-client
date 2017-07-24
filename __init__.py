# -*- coding: utf-8 -*-

# =============================================================================
# Copyright (c) ARMINES / MINES ParisTech 
# Created by Alexandre Barbusse <alexandre.barbusse@gmail.com>
#
# this file is available under the BSD 3-clause License
# (https://opensource.org/licenses/BSD-3-Clause)
# =============================================================================



# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SOSpluginMockup class from file sos_plugin_mockup.py.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .main import SOSpluginMain
    return SOSpluginMain(iface)
