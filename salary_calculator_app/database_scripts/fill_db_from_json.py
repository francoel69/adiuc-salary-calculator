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

BASE_FILE = "../fixtures/"
PERIODO_FILE = BASE_FILE + "initial_data_periodo.json"
DENOMINACION_FILE = BASE_FILE +"initial_data_denominacion.json"
CARGO_FILE = BASE_FILE + "initial_data_cargo.json"
CARGOUNIV_FILE = BASE_FILE + "initial_data_cargouniv.json"
CARGOPREUNIV_FILE = BASE_FILE +"initial_data_cargopreuniv.json"
ANTIGUEDADUNIV_FILE = BASE_FILE + "initial_data_antiguedaduniv.json"
ANTIGUEDADPREUNIV_FILE = BASE_FILE +"initial_data_antiguedadpreuniv.json"

def fill_periodo():
    json_data = open(PERIODO_FILE, 'r')

    data = json.load(json_data)
    json_data.close()

    for item in data:
        if not Periodo.objects.filter(desde=item['fields']['desde'], hasta=item['fields']['hasta']).exists():
            Periodo(pk=item['pk'], desde=item['fields']['desde'], hasta=item['fields']['hasta']).save()

def fill_denominacion():
    json_data = open(DENOMINACION_FILE, 'r')

    data = json.load(json_data)
    json_data.close()

    for item in data:
        if not DenominacionCargo.objects.filter(nombre=item['fields']['nombre']).exists():
            DenominacionCargo(pk=item['pk'], nombre=item['fields']['nombre']).save()

def fill_cargo():
    json_data = open(CARGO_FILE, 'r')

    data = json.load(json_data)
    json_data.close()

    for item in data:
        if not Cargo.objects.filter(pampa=item['fields']['pampa']).exists():
            denominacion = DenominacionCargo.objects.get(pk=item['fields']['denominacion'])
            Cargo(pk=item['pk'], denominacion=denominacion,
                  pampa=item['fields']['pampa'], lu=item['fields']['lu']).save()


if __name__=="__main__":
    fill_periodo()
    fill_denominacion()
    fill_cargo()