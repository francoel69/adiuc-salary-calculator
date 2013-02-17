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

from django import forms
from models import *
import datetime


#Utilizada para filtrar datos en AFamiliaresForm (asignaciones familiares)
def get_concepts_asigf():
    asignaciones = AsignacionFamiliar.objects.all()
    result = list()
    for a in asignaciones:
        c = a.concepto
        result.append(c)
    return list(set(result))


class DetailsForm(forms.Form):
    """Formulario con opciones extras."""

    sis = forms.BooleanField(label=u'Servicio Integral de  Sepelio (SIS)', required=False)
    subsidio_fallecimiento  = forms.BooleanField(label=u'Subsidio por Fallecimiento', required=False)
    fondo_solidario_mayores = forms.IntegerField(label=u'Mayores de 55 años.',
        widget=forms.Select(choices=[(i, i) for i in range(16)]))
    fondo_solidario_menores = forms.IntegerField(label=u'Menores de 55 años.',
        widget=forms.Select(choices=[(i, i) for i in range(16)]))


class AFamiliaresForm(forms.Form):
    """Formulario con opciones específicas opcionales."""

    asig_familiar = forms.ChoiceField(
        label=u'Asignación',
        required=False,
        choices=[(i, unicode(i)) for i in get_concepts_asigf()],
        help_text= u'Seleccione el tipo de asignación.'
    )


class AFamiliaresFormEspecial(forms.Form):
    """Form para ingresar los datos de las asig familiares. Tiene un select
    para ingresar la cantidad de hijos."""

    cant_hijos = forms.IntegerField(
        label=u'Cantidad de Hijos',
        required=False,
        widget=forms.Select(choices=[(i, i) for i in range(16)]),
        help_text=u'Seleccione el tipo de asignación'
    )


class ImpuestoGananciasForm(forms.Form):
    """Formulario para que el usuario ingrese datos referidos al calculo del impuesto a las ganancias"""

    estado_civil = forms.ChoiceField(
        label=u'Estado Civil',
        choices=[(1, u'Soltero/a'), (2, u'Casado/a'), (3, u'Divorciado/a'), (4, u'Viudo/a')]
    )
    conyuge = forms.ChoiceField(
        label=u'En caso de ser casado, ¿El salario neto de su cónyuge supera los $12960 anuales?',
        choices=[(2, 'No'), (1, u'Sí')]
    )
    nro_hijos_menores_24 = forms.ChoiceField(
        label=u'N° de hijos/hijastros menores de 24 años o incapacitados para el trabajo',
        choices=[(i, i) for i in range(15)]
    )
    nro_descendientes = forms.ChoiceField(
       label=u'N° de nietos/bisnietos menores de 24 años o incapacitados para el trabajo',
        choices=[(i, i) for i in range(15)]
    )
    nro_ascendientes = forms.ChoiceField(
       label=u'N° de padres, padrastros y abuelos incapacitados para el trabajo',
        choices=[(i, i) for i in range(6)]
    )
    nro_suegros_yernos_nueras = forms.ChoiceField(
        label=u'N° de suegro/a, yernos/nueras menores de 24 años o incapacitados para el trabajo',
        choices=[(i, i) for i in range(6)]
    )


class CommonForm(forms.Form):
    """Formulario para el cálculo de salario docente. Contiene todos los valores
    que dependen de la persona y no de cada cargo por separado."""

    fecha = forms.DateField(
        label=u'Periodo a calcular',
        initial=datetime.date.today,
        help_text=u'Seleccione una fecha para hacer el cálculo del salario.'
    )

    antiguedad = forms.ChoiceField(
        label=u'Antigüedad', 
        choices=[(i, unicode(i)) for i in 
            range(0, max(AntiguedadUniversitaria.objects.all()[AntiguedadUniversitaria.objects.count()-1].anio,
            AntiguedadPreUniversitaria.objects.all()[AntiguedadPreUniversitaria.objects.count()-1].anio)+1)
        ],
        #choices=[(i, unicode(i)) for i in range(0, 24)],
        help_text=u'Ingrese su antigüedad docente'
    )

    master = forms.BooleanField(label=u'Añadir Título de Maestría', required=False)
    doctorado = forms.BooleanField(label=u'Añadir Título de Doctorado', required=False)

    afiliado = forms.BooleanField(label=u'Afiliado a ADIUC', required=False)
    daspu = forms.BooleanField(label=u'Considerar servicios DASPU', required=False)
    ganancias = forms.BooleanField(label=u'Considerar Impuesto a las Ganancias', required=False)


class CargoUnivForm(forms.Form):
    """Formulario de calculo de salario docente para docentes universitarios."""

    cargo = forms.ModelChoiceField(
        label=u'Cargo',
        queryset=CargoUniversitario.objects.all(),
        empty_label=None,
        help_text=u'Ingrese el nombre del cargo.'
    )


class CargoPreUnivForm(forms.Form):
    """Formulario de calculo de salario docente para docentes Pre-universitarios."""

    cargo = forms.ModelChoiceField(label=u'Cargo', queryset=CargoPreUniversitario.objects.all(), empty_label=None,
       widget=forms.Select(attrs={'onChange': 'show_horas(this)', 'onLoad':'show_horas(this)', 'onKeyUp':'this.blur();this.focus();'}),
       help_text=u'Ingrese el nombre del cargo.'
    )

    horas = forms.FloatField(label=u'Horas de trabajo', min_value=0., max_value=99., initial=1., required=True,
        widget=forms.TextInput(attrs={'maxlength':'5', 'style':'width: 50px;'}),
        help_text=u'Ingrese la cantidad de horas asociadas al cargo.'
    )

    pago_por_horas_info = forms.ChoiceField(
        required=False, 
        choices=[(unicode(c.id), unicode(c.pago_por_hora))  for c in CargoPreUniversitario.objects.all()],
        widget=forms.Select(attrs={'style':'display: none;'})
    )

