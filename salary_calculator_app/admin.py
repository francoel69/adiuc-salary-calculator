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

from salary_calculator_app.models import *
from django.contrib import admin

admin.site.register(SalarioBasico)
admin.site.register(DenominacionCargo)
admin.site.register(CargoUniversitario)
admin.site.register(CargoPreUniversitario)

admin.site.register(GarantiaSalarialUniversitaria)
admin.site.register(GarantiaSalarialPreUniversitaria)

admin.site.register(AntiguedadUniversitaria)
admin.site.register(AntiguedadPreUniversitaria)


admin.site.register(Retencion)
admin.site.register(Remuneracion)
admin.site.register(RetencionPorcentual)
admin.site.register(RetencionFija)
admin.site.register(RemuneracionPorcentual)
admin.site.register(RemuneracionFija)
admin.site.register(RemuneracionFijaCargo)

admin.site.register(AsignacionFamiliar)
admin.site.register(FondoSolidario)
admin.site.register(RetencionDaspu)

admin.site.register(ImpuestoGananciasDeducciones)
admin.site.register(ImpuestoGananciasTabla)

admin.site.register(Configuracion)
