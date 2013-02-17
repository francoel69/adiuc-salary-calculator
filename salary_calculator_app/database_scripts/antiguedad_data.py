#!/usr/bin/env python
# -*- coding: utf-8 -*-

#=============================================
#
# Copyright 2012 David Racca and Matias Molina.
#
# This file is part of ADIUC Salary Calculator.
#
# ADIUC Salary Calculator is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published 
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ADIUC Salary Calculator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ADIUC Salary Calculator.  If not, see 
# <http://www.gnu.org/licenses/>.
#
#=============================================

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

#### Objeto Adicional Antiguedad Remuneracion
rem_obj = Remuneracion.objects.get(codigo="30/0")

#################################
# Tabla de antiguedades para cargos Universitarios #
#################################

def addAntiguedadUniv(anio, porcentaje, vigencia_desde, vigencia_hasta):
    if not AntiguedadUniversitaria.objects.filter(anio=anio, porcentaje=porcentaje, vigencia_desde=vigencia_desde, vigencia_hasta=vigencia_hasta).exists():
        AntiguedadUniversitaria(
            remuneracion=rem_obj,
            anio=anio,
            porcentaje=porcentaje,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        ).save()

addAntiguedadUniv(
    anio=0,
    porcentaje=20.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=1,
    porcentaje=20.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=2,
    porcentaje=20.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=5,
    porcentaje=30.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=7,
    porcentaje=40.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=10,
    porcentaje=50.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=12,
    porcentaje=60.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=15,
    porcentaje=70.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=17,
    porcentaje=80.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=20,
    porcentaje=100.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=22,
    porcentaje=110.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadUniv(
    anio=24,
    porcentaje=120.,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########

###################################
# Tabla de antiguedades para cargos Preuniversitarios#
###################################
def addAntiguedadPreUniv(anio, porcentaje, vigencia_desde, vigencia_hasta):
    if not AntiguedadPreUniversitaria.objects.filter(anio=anio, porcentaje=porcentaje, vigencia_desde=vigencia_desde, vigencia_hasta=vigencia_hasta).exists():
        AntiguedadPreUniversitaria(
            remuneracion=rem_obj,
            anio=anio,
            porcentaje=porcentaje,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        ).save()

addAntiguedadPreUniv(
    anio=0,
    porcentaje=0,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=1,
    porcentaje=10,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=2,
    porcentaje=15,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=5,
    porcentaje=30,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=7,
    porcentaje=40,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=10,
    porcentaje=50,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=12,
    porcentaje=60,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=15,
    porcentaje=70,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=17,
    porcentaje=80,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=20,
    porcentaje=100,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=22,
    porcentaje=110,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)
###########
addAntiguedadPreUniv(
    anio=24,
    porcentaje=120,
    vigencia_desde=date(2012, 1, 1),
    vigencia_hasta=date(2012, 12, 31)
)


### Llena los "huecos" de las tablas de antiguedades.

# WARNING: Usar con cuidado. Tener especial cuidado en los casos en que
# hay antiguedades repetidas dentro del rango de fechas de vigencias.

# Universitarias
def completeAntiguedadUniv(vigencia_desde, vigencia_hasta):

    antunivs = AntiguedadUniversitaria.objects.filter(vigencia_desde=vigencia_desde, vigencia_hasta=vigencia_hasta).order_by('-anio')

    if antunivs.count()>0:
        prev = antunivs[0]
        antunivs = antunivs.exclude(id=prev.id).order_by('-anio')
        for ant in antunivs:
            if ant.anio < prev.anio:
                for anio in range(ant.anio+1, prev.anio):
                    new_ant = AntiguedadUniversitaria(
                        remuneracion=rem_obj,
                        anio=anio,
                        porcentaje=ant.porcentaje,
                        vigencia_desde=vigencia_desde,
                        vigencia_hasta=vigencia_hasta
                    )
                    new_ant.save()
            prev = ant

# PreUniversitarias
def completeAntiguedadPreUniv(vigencia_desde, vigencia_hasta):

    antunivs = AntiguedadPreUniversitaria.objects.filter(vigencia_desde=vigencia_desde, vigencia_hasta=vigencia_hasta).order_by('-anio')

    if antunivs.count()>0:
        prev = antunivs[0]
        antunivs = antunivs.exclude(id=prev.id).order_by('-anio')
        for ant in antunivs:
            if ant.anio < prev.anio:
                for anio in range(ant.anio+1, prev.anio):
                    new_ant = AntiguedadPreUniversitaria(
                        remuneracion=rem_obj,
                        anio=anio,
                        porcentaje=ant.porcentaje,
                        vigencia_desde=vigencia_desde,
                        vigencia_hasta=vigencia_hasta
                    )
                    new_ant.save()
            prev = ant

completeAntiguedadUniv(date(2012, 1, 1), date(2012, 12, 31))
completeAntiguedadPreUniv(date(2012, 1, 1), date(2012, 12, 31))
