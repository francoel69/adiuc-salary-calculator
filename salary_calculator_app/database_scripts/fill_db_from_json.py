#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: Franco Rodriguez (ffrodriguez@famaf.unc.edu.ar)
# date: 18/03/2013

import json
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

PERIODO_FILE = "../fixtures/initial_data_periodo.json"

if __name__=="__main__":
    json_data = open(PERIODO_FILE, 'r')
    p = Periodo.objects.filter
    print p
    data = json.load(json_data)
    json_data.close()

    for item in data:
        if not Periodo.objects.filter(desde=item['fields']['desde'], hasta=item['fields']['hasta']).exists():
            Periodo(desde=item['desde'], hasta=item['hasta']).save()
