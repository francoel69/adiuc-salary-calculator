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


def add_retencion(codigo, nombre, aplicacion, modo):

    r = None
    if not Retencion.objects.filter(codigo=codigo, nombre=nombre, aplicacion=aplicacion, modo=modo).exists():
        r = Retencion(codigo=codigo, nombre=nombre, aplicacion=aplicacion, modo=modo)
        r.save()
    else:
        r = Retencion.objects.get(codigo=codigo, nombre=nombre, aplicacion=aplicacion, modo=modo)
    return r


def add_remuneracion(codigo, nombre, aplicacion, modo, remunerativo, bonificable):

    r = None
    if not Remuneracion.objects.filter(
        codigo=codigo,
        nombre=nombre,
        aplicacion=aplicacion,
        modo=modo,
        remunerativo=remunerativo,
        bonificable=bonificable).exists():
            r = Remuneracion(
                codigo=codigo,
                nombre=nombre,
                aplicacion=aplicacion,
                modo=modo,
                remunerativo=remunerativo,
                bonificable=bonificable)
            r.save()
    else:
        r = Remuneracion.objects.get(
                codigo=codigo,
                nombre=nombre,
                aplicacion=aplicacion,
                modo=modo,
                remunerativo=remunerativo,
                bonificable=bonificable
        )
    return r


def add_retencion_porcentual(retencion, porcentaje, vigencia_desde, vigencia_hasta):

    if not RetencionPorcentual.objects.filter(
        retencion=retencion,
        porcentaje=porcentaje,
        vigencia_desde=vigencia_desde,
        vigencia_hasta=vigencia_hasta).exists(
    ):
        r = RetencionPorcentual(
            retencion=retencion,
            porcentaje=porcentaje,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        )
        r.save()


def add_remuneracion_porcentual(remuneracion, porcentaje, vigencia_desde, vigencia_hasta):

    if not RemuneracionPorcentual.objects.filter(
        remuneracion=remuneracion,
        porcentaje=porcentaje,
        vigencia_desde=vigencia_desde,
        vigencia_hasta=vigencia_hasta).exists(
    ):
        r = RemuneracionPorcentual(
            remuneracion=remuneracion,
            porcentaje=porcentaje,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        )
        r.save()


def add_retencion_fija(retencion, valor, vigencia_desde, vigencia_hasta):

    if not RetencionFija.objects.filter(
        retencion=retencion,
        valor=valor,
        vigencia_desde=vigencia_desde,
        vigencia_hasta=vigencia_hasta).exists(
    ):
        r = RetencionFija(
            retencion=retencion,
            valor=valor,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        )
        r.save()


def add_remuneracion_fija(remuneracion, valor, vigencia_desde, vigencia_hasta):

    if not RemuneracionFija.objects.filter(
        remuneracion=remuneracion,
        valor=valor,
        vigencia_desde=vigencia_desde,
        vigencia_hasta=vigencia_hasta).exists(
    ):
        r = RemuneracionFija(
            remuneracion=remuneracion,
            valor=valor,
            vigencia_desde=vigencia_desde,
            vigencia_hasta=vigencia_hasta
        )
        r.save()


##### VIGENCIAS
vigencia_desde = date(2012, 1, 1)
vigencia_hasta = date(2012, 12, 31)



##### Retenciones Porcentuales

# Retencion DASPU
r = add_retencion(
    codigo=u"40/0",
    nombre= u"DASPU",
    aplicacion=u"T",
    modo=u"C"
)
add_retencion_porcentual(
    retencion=r,
    porcentaje= 3.0,
    vigencia_desde=vigencia_desde,
    vigencia_hasta=vigencia_hasta
)

####
r = add_retencion(
    codigo=u"20/3",
    nombre= u"Aporte Fondo Adic. Universitario",
    aplicacion=u"U",
    modo=u"C"
)
add_retencion_porcentual(
    retencion = r,
    porcentaje = 2.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_retencion(
    codigo=u"20/9",
    nombre= u"Jubilación Régimen Especial",
    aplicacion=u"T",
    modo=u"C"
)
add_retencion_porcentual(
    retencion = r,
    porcentaje = 11.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_retencion(
    codigo="21/0",
    nombre= u"Caja Complementaria de Jub.",
    aplicacion=u"T",
    modo=u"C"
)
add_retencion_porcentual(
    retencion = r,
    porcentaje = 4.5,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_retencion(
    codigo=u"22/0",
    nombre= u"Ley 19032 Obra Soc. Jubilados",
    aplicacion=u"T",
    modo=u"C"
)
add_retencion_porcentual(
    retencion = r,
    porcentaje = 3.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_retencion(
    codigo=u"64/0",
    nombre= u"ADIUC - Afiliación",
    aplicacion=u"T",
    modo=u"C"
)
add_retencion_porcentual(
    retencion = r,
    porcentaje = 1.5,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)

##### Retenciones Fijas

r = add_retencion(
    codigo=u"DAS/1",
    nombre= u"Sistema Integral de Sepelio (SIS)",
    aplicacion=u"T",
    modo=u"P"
)
add_retencion_fija(
    retencion = r,
    valor = 7.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)

###
r = add_retencion(
    codigo=u"DAS/4",
    nombre= u"Fondo Solidario",
    aplicacion=u"T",
    modo=u"P"
)
add_retencion_fija(
    retencion = r,
    valor = 7.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
###
r = add_retencion(
    codigo=u"DAS/2",
    nombre= u"Subsidio por fallecimiento",
    aplicacion=u"T",
    modo=u"P"
)
add_retencion_fija(
    retencion = r,
    valor = 7.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)

###
r = add_retencion(
    codigo=u"77/0",
    nombre= u"Fondo de Becas",
    aplicacion=u"T",
    modo=u"P"
)
add_retencion_fija(
    retencion = r,
    valor = 3.8,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)

###### Remuneraciones Porcentuales
r = add_remuneracion(
    codigo=u"30/0",
    nombre= u"Adicional por Antigüedad",
    aplicacion=u"T",
    modo=u"C",
    remunerativo=True,
    bonificable=False
)
## Ver: antiguedad_data.py
####
r = add_remuneracion(
    codigo=u"51/0",
    nombre= u"Adicional Título Doctorado",
    aplicacion=u"U",
    modo=u"C",
    remunerativo=True,
    bonificable=False
)
add_remuneracion_porcentual(
    remuneracion = r,
    porcentaje = 15.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_remuneracion(
    codigo=u"53/0",
    nombre= u"Adic. Tít. Doctorado Nivel Medio",
    aplicacion=u"P",
    modo=u"C",
    remunerativo=True,
    bonificable=False
)
add_remuneracion_porcentual(
    remuneracion = r,
    porcentaje = 15.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_remuneracion(
    codigo=u"52/0",
    nombre= u"Adicional Título Maestría",
    aplicacion=u"U",
    modo=u"C",
    remunerativo=True,
    bonificable=False
)
add_remuneracion_porcentual(
    remuneracion = r,
    porcentaje = 5.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####
r = add_remuneracion(
    codigo=u"55/0",
    nombre= u"Adic. Tít. Maestría Nivel Medio",
    aplicacion=u"P",
    modo=u"C",
    remunerativo=True,
    bonificable=False
)
add_remuneracion_porcentual(
    remuneracion = r,
    porcentaje = 5.0,
    vigencia_desde = vigencia_desde,
    vigencia_hasta = vigencia_hasta
)
####

###### Remuneraciones Fijas
r = add_remuneracion(
    codigo=u"10/0",
    nombre= u"Sueldo Básico",
    aplicacion=u"T",
    modo=u"C",
    remunerativo=True,
    bonificable=True
)

r = add_remuneracion(
    codigo=u"---",
    nombre= u"Asignación Familiar",
    aplicacion=u"T",
    modo=u"P",
    remunerativo=True,
    bonificable=False
)

r = add_remuneracion(
    codigo = "12/2",
    nombre = "FONID",
    aplicacion = 'P',
    modo = 'C',
    remunerativo = False,
    bonificable = False
)

###### Impuesto a las ganancias
add_retencion(
    codigo = '42/0',
    nombre = 'Impuesto Ganancias',
    aplicacion = 'T',
    modo = 'P'
)
