#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: Franco Rodriguez (ffrodriguez@famaf.unc.edu.ar)
# date: 18/03/2013

import sys
import os
import pdb
from datetime import date
sys.path.append(os.getcwd() + '/../../')

try:
        from salary_calculator import settings
except ImportError:
        import sys
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

from django.core.management import setup_environ
setup_environ(settings)

from salary_calculator_app.models import *

#################################
# Tabla de periodos #
#################################

def addPeriodo(desde, hasta):
    if not Periodo.objects.filter(desde=desde, hasta=hasta).exists():
        Periodo(desde=desde, hasta=hasta).save()

addPeriodo(
    desde=date(2011, 09, 01),
    hasta=date(2012, 02, 29)
)

addPeriodo(
    desde=date(2012, 03, 01),
    hasta=date(2012, 05, 31)
)

addPeriodo(
    desde=date(2012, 06, 01),
    hasta=date(2012, 08, 31)
)

addPeriodo(
    desde=date(2012, 09, 01),
    hasta=date(2020, 12, 31)
)

addPeriodo(
    desde=date(2011, 09, 01),
    hasta=date(2020, 12, 31)
)
