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
# GNU General Public License for more detailss.
#
# You should have received a copy of the GNU General Public License
# along with ADIUC Salary Calculator.  If not, see 
# <http://www.gnu.org/licenses/>.
#
#=============================================

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory

from forms import *
from models import *

# Debugger
import pdb

###############################################
# Hardcoded
###############################################

doc_code = '51/0'
doc_preuniv_code = '53/0'

master_code = '52/0'
master_preuniv_code = '55/0'

garantia_code = '11/5'
garantia_name = u'Garantía Docentes Univ.'

garantia_preuniv_code = '10/7'
garantia_preuniv_name = u'Garantía Nivel Medio'

#fondo_becas_code = '77/0'
#fondo_becas_name = u'Fondo de Becas'

daspu_code = '40/0'

afiliacion_code = '64/0'
afiliacion_name = u'ADIUC - Afiliacion'

sis_code = "DAS/1"
subsidio_fallecimiento_code = "DAS/2"
fs_code="DAS/4"



###############################################
# Helpers
###############################################


def merge_retrem(context1, context2, key):
    """Para mezclar las listas de retenciones/remuneraciones de cada context"""
    r1 = list()
    r2 = list()
    if context1.has_key(key):
        r1 = list(context1[key])
    if context2.has_key(key):
        r2 = list(context2[key])
    result = list(set(r1 + r2))
    
    return result


def add_values_from_contexts(context1, context2, key):
    """Return the plus between context1[key] and context2[key]."""
    v1 = 0.0
    v2 = 0.0
    if context1.has_key(key):
        v1 = context1[key]
    if context2.has_key(key):
        v2 = context2[key]

    return v1 + v2


##############################################
# Views
##############################################

def calculate(request):
    """Vista principal"""

    # Obtengo el objeto de configuracion.
    conf = Configuracion.objects.all()
    if conf.exists():
        conf = conf[0]

    # Permite que aparezcan multiples formularios identicos.
    CargoUnivFormSet = formset_factory(CargoUnivForm, extra=0, max_num=5, can_delete=True)
    CargoPreUnivFormSet = formset_factory(CargoPreUnivForm, extra=0, max_num=5, can_delete=True)
    AFamiliaresFormSet = formset_factory(AFamiliaresForm, extra=0, max_num=10, can_delete=True)

    context = {}

    if request.method == 'POST':

        # Sacamos la info del POST y bindeamos los forms.
        univformset = CargoUnivFormSet(request.POST, prefix='univcargo')
        preunivformset = CargoPreUnivFormSet(request.POST, prefix='preunivcargo')
        commonform = CommonForm(request.POST)
        afamiliaresformset = AFamiliaresFormSet(request.POST, prefix='afamiliares')
        afamiliaresformespecial = AFamiliaresFormEspecial(request.POST)
        detailsform = DetailsForm(request.POST)
        gananciasform = ImpuestoGananciasForm(request.POST)

        if univformset.is_valid() and preunivformset.is_valid() and commonform.is_valid() \
             and afamiliaresformset.is_valid() and afamiliaresformespecial.is_valid() and detailsform.is_valid() and gananciasform.is_valid():

            # Proceso los formularios de cargos.
            context_univ = processUnivFormSet(commonform, univformset)
            context_preuniv = processPreUnivFormSet(commonform, preunivformset)

            # Control de errores
            if context_univ.has_key('error_msg'):
                context['error_msg'] = context_univ['error_msg']
                return render_to_response('salary_calculated.html', context)
            if context_preuniv.has_key('error_msg'):
                context['error_msg'] = context_preuniv['error_msg']
                return render_to_response('salary_calculated.html', context)

            # Sumo los totales de remuneraciones y retenciones de ambos contexts.
            total_rem = add_values_from_contexts(context_univ, context_preuniv, 'total_rem')
            total_ret = add_values_from_contexts(context_univ, context_preuniv, 'total_ret')
            total_bruto = add_values_from_contexts(context_univ, context_preuniv, 'total_bruto')
            total_neto = add_values_from_contexts(context_univ, context_preuniv, 'total_neto')

            # Hago el merge de los dos contexts.
            context['total_rem'] = total_rem
            context['total_ret'] = total_ret
            context['total_bruto'] = total_bruto
            context['total_neto'] = total_neto
            context['fecha'] = commonform.cleaned_data['fecha']

            context['lista_res'] = list()
            if context_univ.has_key('lista_res'):
                context['lista_res'].extend(context_univ['lista_res'])
            if context_preuniv.has_key('lista_res'):
                context['lista_res'].extend(context_preuniv['lista_res'])

            # Calculo de las remuneraciones y retenciones que son por persona.
            # Esto modifica el contexto.
            afiliacion_daspu = commonform.cleaned_data['daspu']
            afiliacion_adiuc = commonform.cleaned_data['afiliado']
            calcular_ganancias = commonform.cleaned_data['ganancias']
            context = calculateRemRetPorPersona(
                context,
                afiliacion_adiuc,
                afiliacion_daspu,
                calcular_ganancias,
                afamiliaresformset,
                afamiliaresformespecial,
                detailsform,
                gananciasform,
                conf
                )

            # Renderizo el template con el contexto.
            return render_to_response('salary_calculated.html', context)

        else:
            context['univformset'] = univformset
            context['preunivformset'] = preunivformset
            context['commonform'] = commonform
            context['afamiliaresformset'] = afamiliaresformset
            context['afamiliaresformespecial'] = afamiliaresformespecial
            context['detailsform'] = detailsform
            context['gananciasform'] = gananciasform
            context['conf'] = conf

    else:

        # Creamos formularios vacios (sin bindear) y los mandamos.
        univformset = CargoUnivFormSet(prefix='univcargo')
        preunivformset = CargoPreUnivFormSet(prefix='preunivcargo')
        commonform = CommonForm()
        afamiliaresformset = AFamiliaresFormSet(prefix='afamiliares')
        afamiliaresformespecial = AFamiliaresFormEspecial()
        detailsform = DetailsForm()
        gananciasform = ImpuestoGananciasForm()

        context['univformset'] = univformset
        context['preunivformset'] = preunivformset
        context['commonform'] = commonform
        context['afamiliaresformset'] = afamiliaresformset
        context['afamiliaresformespecial'] = afamiliaresformespecial
        context['detailsform'] = detailsform
        context['gananciasform'] = gananciasform
        context['conf'] = conf

    return render_to_response('calculate.html', context)



##############################################
# Form processing
##############################################

def processAFamiliaresFormSet(context, afamiliaresformset, afamiliaresformespecial, conf):
    """ Procesa un formet con formularios de asignaciones familiares.
        Retorna una tupla con dos elementos:
            * El primero, una lista con todas las asignaciones.
            * El segundo, la suma total correspondiente a la primer lista."""

    fecha = context['fecha']
    total_bruto = context['total_bruto']

    afamiliares_list = list()
    total = 0.0

    if conf.asig_fam_solo_opc_hijo:
        cant_hijos = afamiliaresformespecial.cleaned_data['cant_hijos']
        for i in range(cant_hijos):
            aform = AFamiliaresForm({'asig_familiar' : u'Hijo'})
            # Para que django convierta los datos del form a python data.
            aform.is_valid()
            afamiliaresformset.forms.append(aform)

    for afamiliaresform in afamiliaresformset:
        # No analizamos los forms que fueron borrados por el usuario.
        if afamiliaresform in afamiliaresformset.deleted_forms:
            continue

        afamiliar_concepto = afamiliaresform.cleaned_data['asig_familiar']

        # Tomo las asignaciones familiares del mismo concepto, cateogria y fecha adecuada.
        afamiliares = AsignacionFamiliar.objects.filter(
            concepto = afamiliar_concepto,
            valor_min__lte = total_bruto,
            valor_max__gte = total_bruto,
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha
        )

        # De todas las anteriores tomo la de fecha vigente.
        if afamiliares:
            afamiliar = afamiliares.order_by('vigencia_hasta')[afamiliares.count()-1]
            afamiliares_list.append(afamiliar)
            total += afamiliar.valor

    return (afamiliares_list,total)


def processDetailsForm(context, detailsform):

    fecha = context['fecha']
    total_rem = context['total_rem']
    total_ret = context['total_ret']
    total_bruto = context['total_bruto']
    total_neto = context['total_neto']
    
    sis = detailsform.cleaned_data['sis']
    sf = detailsform.cleaned_data['subsidio_fallecimiento']
    fs_mayores = detailsform.cleaned_data['fondo_solidario_mayores']
    fs_menores = detailsform.cleaned_data['fondo_solidario_menores']
    
    result = {}
  
    #en principio estos datos son retenciones por persona
    #los datos se guardan indicando esa categoria para luego ser procesados en..  (ej: l656+ ) 

    if fs_mayores > 0.0:
        fs_objs= FondoSolidario.objects.filter(
            retencion__codigo=fs_code,
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha,
            concepto='Fondo solidario para una persona (mayor a 55 años)'
            )
        if not fs_objs.exists():
            result["error_msg"] = "No hay información sobre Fondo solidario para personas mayores de 55 años."
        else:
            fs_obj = fs_objs.order_by('vigencia_hasta')[fs_objs.count()-1]
            importe = fs_obj.valor * fs_mayores
            result['fs_mayores'] = ('retencion_fija_persona',fs_obj,importe)

    if fs_menores>0.0:
        if fs_menores == 1:
            query='Fondo solidario para una persona (menor a 55 años)'
        elif fs_menores == 2:
            query='Fondo solidario para dos personas (menor a 55 años)'
        elif fs_menores == 3:
            query='Fondo solidario para tres personas (menor a 55 años)'
        elif fs_menores ==4:
            query='Fondo solidario para cuatro personas (menor a 55 años)'
        else:
            query='Fondo solidario para cinco personas o más (menor a 55 años)'
            
        fs_objs= FondoSolidario.objects.filter(
            retencion__codigo=fs_code,
                vigencia_desde__lte=fecha,
                vigencia_hasta__gte=fecha,
                concepto=query
            )
        if not fs_objs.exists():
            result["error_msg"] = "No hay información sobre Fondo solidario"
        else:
            fs_obj = fs_objs.order_by('vigencia_hasta')[fs_objs.count()-1]
            importe = fs_obj.valor
            result['fs_menores'] = ('retencion_fija_persona',fs_obj,importe)

    if sis:    
        sis_objs= RetencionFija.objects.filter(
                retencion__codigo=sis_code,
                vigencia_desde__lte=fecha,
                vigencia_hasta__gte=fecha
            )
        if not sis_objs.exists():
            result["error_msg"] = "No existe informacion sobre Seguro Integral de Sepelio."
        else:
            sis_obj = sis_objs.order_by('vigencia_hasta')[sis_objs.count()-1]
            result['sis'] = ('retencion_fija_persona',sis_obj,sis_obj.valor)

    if sf:    
        sf_objs= RetencionFija.objects.filter(
                retencion__codigo=subsidio_fallecimiento_code,
                vigencia_desde__lte=fecha,
                vigencia_hasta__gte=fecha
            )
        if not sf_objs.exists():
            result["error_msg"] = "No existe informacion sobre Subsidio por Fallecimiento."
        else:
            sf_obj = sf_objs.order_by('vigencia_hasta')[sf_objs.count()-1]
            result['sf'] = ('retencion_fija_persona',sf_obj,sf_obj.valor)

    return result

def calculateDASPU(fecha,total_bruto):
    
    daspu_context={}
    daspu_importe = 0.0
    daspu_extra = 0.0

    rets_porc_daspu = RetencionPorcentual.objects.filter(
        retencion__codigo =daspu_code,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
        )
    if rets_porc_daspu.exists():
        r = rets_porc_daspu.order_by('vigencia_hasta')[rets_porc_daspu.count()-1]

        daspu_objs = RetencionDaspu.objects.filter(
            retencion=r,
            )
        if not daspu_objs.exists():
            context["error_msg"] = "No existe informacion sobre afiliaciones para DASPU.\n"
        else:
            daspu_obj = daspu_objs[daspu_objs.count()-1]
            p = daspu_obj.retencion.porcentaje
            p_min = daspu_obj.porcentaje_minimo

            # Corroborar si no cubre el minimo de del cargo ayudante D.S.E. sin antiguedad.
            basicos = SalarioBasico.objects.filter(
                cargo=daspu_obj.cargo_referencia,
                vigencia_desde__lte=fecha,
                vigencia_hasta__gte=fecha
                )
            if not basicos.exists():
                context['error_msg']='No se encuentra información la salarial requerida para el cálculo.'
            else:
                basico = basicos.order_by('vigencia_hasta')[basicos.count()-1]
                basico = basico.valor
                daspu_importe += total_bruto * p / 100.0
                tope_min = basico * p_min / 100.0
            
                daspu_context['daspu_importe'] = daspu_importe                
            
                if daspu_importe < tope_min:
                    daspu_extra = tope_min - daspu_importe
                    daspu_context['daspu_extra'] = daspu_extra
                    daspu_context['daspu_importe'] = tope_min
                    daspu_importe = tope_min

                daspu_context['daspu'] = daspu_obj
        
    return daspu_context

def calculateRemRetPorPersona(context, es_afiliado, afiliacion_daspu, calcular_ganancias,
afamiliaresformset, afamiliaresformespecial, detailsform, gananciasform, conf):

    fecha = context['fecha']
    total_rem = context['total_rem']
    total_ret = context['total_ret']
    total_bruto = context['total_bruto']
    total_neto = context['total_neto']

    # Retenciones / Remuneraciones que son por persona para cargos Universitarios.
    ret_rem_persona = get_retenciones_remuneraciones('U', 'P', fecha)
    ret_fijas_persona_univ = ret_rem_persona['ret_fijas']
    ret_porc_persona_univ = ret_rem_persona['ret_porcentuales']
    rem_fijas_persona_univ = ret_rem_persona['rem_fijas']
    rem_porc_persona_univ = ret_rem_persona['rem_porcentuales']

    # Retenciones / Remuneraciones que son por persona para cargos Preuniversitarios.
    ret_rem_persona = get_retenciones_remuneraciones('P', 'P', fecha)
    ret_fijas_persona_preuniv = ret_rem_persona['ret_fijas']
    ret_porc_persona_preuniv = ret_rem_persona['ret_porcentuales']
    rem_fijas_persona_preuniv = ret_rem_persona['rem_fijas']
    rem_porc_persona_preuniv = ret_rem_persona['rem_porcentuales']

    # Quito los duplicados, si hay, entre univ y preuniv para las ret/rem por persona
    ret_fp = ret_fijas_persona_univ | ret_fijas_persona_preuniv
    ret_pp  = ret_porc_persona_univ | ret_porc_persona_preuniv
    rem_fp = rem_fijas_persona_univ | rem_fijas_persona_preuniv
    rem_pp  = rem_porc_persona_univ | rem_porc_persona_preuniv

    # Calculo las retenciones/remuneraciones que son por persona.
    acum_ret = 0.0
    acum_rem = 0.0

    ret_porc_persona = list()
    rem_porc_persona = list()
    ret_fijas_persona = list()
    rem_fijas_persona = list()

    # Proceso el formulario de asignacion familiar.

    afamiliares_list, total_afamiliares = processAFamiliaresFormSet(context, afamiliaresformset, afamiliaresformespecial, conf)

    acum_rem += total_afamiliares
    
    for ret in ret_pp:
        importe = (total_bruto * ret.porcentaje / 100.0)
        acum_ret += importe
        ret_porc_persona.append( (ret, importe) )

    for ret in ret_fp:
        acum_ret += ret.valor
        ret_fijas_persona.append( (ret, ret.valor) )

    for rem in rem_pp:
        importe = (total_bruto * ret.porcentaje / 100.0)
        acum_rem += importe
        rem_porc_persona.append( (rem, importe) )

    for rem in rem_fp:
        importe = rem.valor
        acum_rem += importe
        rem_fijas_persona.append( (rem, rem.valor) )



    #### Calculo del impuesto a las ganancias
    if calcular_ganancias:

        importe_ganancias = -1
        remuneracion_bruta = total_bruto*13 # El total bruto anual + el aguinaldo

        ## Deducciones generales.
        # Busco la jubilacion, obra social, ley 19.032 y cuota sindical (adiuc)
        deducciones_generales = 0.0
        cant_cargos = len(context['lista_res'])
        for ret, importe in ret_porc_persona:
            if ret.retencion.codigo == u'64/0':
                deducciones_generales += importe
        for form_res in context['lista_res']:
            for ret, importe in form_res['retenciones']:
                if ret.retencion.codigo == u'22/0' or ret.retencion.codigo == u'21/0' or ret.retencion.codigo == u'20/9':
                    deducciones_generales += importe
        deducciones_generales *= 12 # el total anual.

        ## Deducciones especiales o tecnicas.

        deducciones_especiales = 0.0
        estado_civil = gananciasform.cleaned_data['estado_civil']
        conyuge = gananciasform.cleaned_data['conyuge']
        nro_hijos_menores_24 = float(gananciasform.cleaned_data['nro_hijos_menores_24'])
        nro_descendientes = float(gananciasform.cleaned_data['nro_descendientes'])
        nro_ascendientes = float(gananciasform.cleaned_data['nro_ascendientes'])
        nro_suegros_yernos_nueras = float(gananciasform.cleaned_data['nro_suegros_yernos_nueras'])
        
        deducciones_objs = ImpuestoGananciasDeducciones.objects.filter(
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha
        )
        if deducciones_objs.exists():
            deducciones_obj = deducciones_objs.order_by('vigencia_hasta')[deducciones_objs.count()-1]
            deducciones_especiales += deducciones_obj.ganancia_no_imponible
            if estado_civil == 2 and conyuge == 1:
                deducciones_especiales += deducciones_obj.por_conyuge
            deducciones_especiales += deducciones_obj.por_hijo_menor_24_anios * nro_hijos_menores_24
            deducciones_especiales += deducciones_obj.por_descendiente * nro_descendientes
            deducciones_especiales += deducciones_obj.por_ascendiente * nro_ascendientes
            deducciones_especiales += deducciones_obj.por_suegro_yerno_nuera * nro_suegros_yernos_nueras
            deducciones_especiales += deducciones_obj.deduccion_especial

        ganancia_neta = remuneracion_bruta - deducciones_generales - deducciones_especiales
        ganancias_tablas = ImpuestoGananciasTabla.objects.filter(
            ganancia_neta_min__lte = ganancia_neta,
            ganancia_neta_max__gte = ganancia_neta,
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha
        )
        if ganancias_tablas.exists():
            ganancias_tabla = ganancias_tablas.order_by('vigencia_hasta')[ganancias_tablas.count()-1]
            importe_ganancias = ganancias_tabla.impuesto_fijo + (ganancia_neta - ganancias_tabla.sobre_exedente_de) * (ganancias_tabla.impuesto_porcentual / 100)

        ganancias_retencion_objs = Retencion.objects.filter(codigo='42/0')
        if importe_ganancias >= 0 and ganancias_retencion_objs.exists():
            new_ret_fija = RetencionFija(retencion=ganancias_retencion_objs[0], valor=importe_ganancias / 12, vigencia_desde=fecha, vigencia_hasta=fecha)
            ret_fijas_persona.append( (new_ret_fija, new_ret_fija.valor) )
            acum_ret += importe_ganancias / 12



    total_ret += acum_ret
    total_rem += acum_rem

    total_neto = total_neto - acum_ret + acum_rem

    context['ret_fijas_persona'] = ret_fijas_persona
    context['ret_porc_persona'] = ret_porc_persona
    context['rem_fijas_persona'] = rem_fijas_persona
    context['rem_porc_persona'] = rem_porc_persona
    context['afamiliares_list'] = afamiliares_list

    context['total_bruto'] = total_bruto
    context['total_neto'] = total_neto
    context['total_ret'] = total_ret
    context['total_rem'] = total_rem

    return context


def get_retenciones_remuneraciones(aplicacion, modo, fecha):
    """Devuelve en un dict las ret fijas, ret porc, rem fijas, rem porc
    que matchean la aplicacion, modo y fecha dadas."""

    result = dict()

    # Filtro las Retenciones / Remuneraciones que son por persona (no por cargo).
    ret_fijas = RetencionFija.objects.filter(
        retencion__aplicacion=aplicacion,
        retencion__modo=modo,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    ret_porcentuales = RetencionPorcentual.objects.filter(
        retencion__aplicacion=aplicacion,
        retencion__modo=modo,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    rem_fijas = RemuneracionFija.objects.filter(
        remuneracion__aplicacion=aplicacion,
        remuneracion__modo=modo,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    rem_porcentuales  = RemuneracionPorcentual.objects.filter(
        remuneracion__aplicacion=aplicacion,
        remuneracion__modo=modo,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    result['ret_fijas'] = ret_fijas
    result['ret_porcentuales'] = ret_porcentuales
    result['rem_fijas'] = rem_fijas
    result['rem_porcentuales'] = rem_porcentuales

    return result



def filter_doc_masters_from_rem_porcentuales(rem_porcentuales, has_doctorado, has_master, aplicacion):
    """Elimina las remuneraciones porcentuales asociadas a titulos adicionales segun
    lo que haya especificado el usuario."""

    m_code = ""
    d_code = ""

    if aplicacion == 'U':
        m_code = master_code
        d_code = doc_code
    elif aplicacion == 'P':
        m_code = master_preuniv_code
        d_code = doc_preuniv_code

    if has_doctorado:
        rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo=m_code)
    elif has_master:
        rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo=d_code)
    else:
        rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo=d_code)
        rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo=m_code)

    return rem_porcentuales



def processUnivFormSet(commonform, univformset):
    """Procesa un formset con formularios de cargos universitarios. Retorna un context"""

    antiguedad = commonform.cleaned_data['antiguedad']
    fecha = commonform.cleaned_data['fecha']
    has_doctorado = commonform.cleaned_data['doctorado']
    has_master = commonform.cleaned_data['master']
    #afiliacion adiuc:
    es_afiliado = commonform.cleaned_data['afiliado']

    context = {}

    #Guardo en esta lista un diccionario para cada formulario procesado
    lista_res = list()

    total_rem = 0.0
    total_ret = 0.0
    total_bruto = 0.0
    total_neto = 0.0

    # Obtengo las Retenciones / Remuneraciones que son para cargos universitarios.
    ret_rem_cargo_univ = get_retenciones_remuneraciones('U', 'C', fecha)
    ret_rem_cargo_all = get_retenciones_remuneraciones('T', 'C', fecha)
    ret_fijas = ret_rem_cargo_univ['ret_fijas'] | ret_rem_cargo_all['ret_fijas'] # El operador | es la union de qs. & es la interseccion.
    ret_porcentuales = ret_rem_cargo_univ['ret_porcentuales'] | ret_rem_cargo_all['ret_porcentuales']
    rem_fijas = ret_rem_cargo_univ['rem_fijas'] | ret_rem_cargo_all['rem_fijas']
    rem_porcentuales = ret_rem_cargo_univ['rem_porcentuales'] | ret_rem_cargo_all['rem_porcentuales']

    # Obtengo la Antiguedad
    antiguedades = AntiguedadUniversitaria.objects.filter(
        anio=antiguedad,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    antiguedad = None
    if not antiguedades.exists():
        context['error_msg'] = u'No existe información de Salarios Básicos \
        para los datos ingresados. Por favor intente con otros datos.'
        return context
    else:
        antiguedad = antiguedades.order_by('vigencia_hasta')[antiguedades.count()-1]
        for ant in antiguedades:
            rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = ant.remuneracion.codigo)

    for univform in univformset:

        # No analizamos los forms que fueron borrados por el usuario.
        if univform in univformset.deleted_forms:
            continue

        cargo_obj = univform.cleaned_data['cargo']

        ###### Salario Bruto.
        basicos = SalarioBasico.objects.filter(cargo=cargo_obj, vigencia_desde__lte=fecha, vigencia_hasta__gte=fecha)
        basico = None
        if not basicos.exists():
            context['error_msg'] = u'No existe información de Salarios Básicos \
            para los datos ingresados. Por favor intente con otros datos.'
            return context
        else:
            basico = basicos.order_by('vigencia_hasta')[basicos.count()-1]
            for bas in basicos:
                rem_fijas = rem_fijas.exclude(remuneracion__codigo = bas.remuneracion.codigo)
        antiguedad_importe = basico.valor * antiguedad.porcentaje / 100.0
        salario_bruto = basico.valor + antiguedad_importe


        ###### El Neto se calcula del bruto restando las retenciones y sumando las remuneraciones.

        ret_list = list()  # Con tuplas de la forma (obj retencion, importe).
        rem_list = list()  # Con tuplas (obj remuneracion, importe).

        acum_ret = 0. # El acumulado de todo lo que hay que descontarle al bruto.
        acum_rem = 0. # El acumulado de todo lo que hay que sumarle.

        # Adicional titulo doctorado (cod 51), Adicional titulo maestria (cod 52)
        rem_porcentuales = filter_doc_masters_from_rem_porcentuales(rem_porcentuales, has_doctorado, has_master, 'U')

        #daspu se calcula aparte
        ret_porcentuales = ret_porcentuales.exclude(retencion__codigo = daspu_code)
        
        if not es_afiliado:
            ret_porcentuales = ret_porcentuales.exclude(retencion__codigo = afiliacion_code)

        ## Retenciones / Remuneraciones NO especiales:
        for ret in ret_porcentuales:
            importe = salario_bruto * ret.porcentaje / 100.
            acum_ret += importe
            ret_list.append( (ret, importe) )

        for ret in ret_fijas:
            acum_ret += ret.valor
            ret_list.append( (ret, ret.valor) )

        for rem in rem_porcentuales:
            importe = salario_bruto * rem.porcentaje / 100.
            acum_rem += importe
            rem_list.append( (rem, importe) )

        for rem in rem_fijas:
            acum_rem += rem.valor
            rem_list.append( (rem, rem.valor) )

        # Calculo afiliacion daspu
        daspu_context = calculateDASPU(fecha,salario_bruto)
        if daspu_context.has_key('error_msg'):
            context['error_msg'] = "\n"+daspu_context['error_msg']

        daspu_importe = daspu_context['daspu_importe']
        acum_ret += daspu_importe

        ###### Salario Neto.
        salario_neto = salario_bruto - acum_ret + acum_rem

        ## Garantia salarial.
        garantias_salariales = GarantiaSalarialUniversitaria.objects.filter(cargo=cargo_obj, vigencia_desde__lte=fecha, vigencia_hasta__gte=fecha)

        if garantias_salariales.exists():

            garantia_obj = garantias_salariales.order_by('vigencia_hasta')[garantias_salariales.count()-1]
            valor_minimo = garantia_obj.valor_minimo

            if salario_neto < valor_minimo:
  
                if garantia_obj.antiguedad_min <= antiguedad.anios and antiguedad.anios < garantia_obj.antiguedad_max:

                    if has_doctorado:
                        valor = garantia_obj.valor_doctorado
                    elif has_master:
                        valor = garantia_obj.valor_master
                    else:
                        valor = garantia_obj.valor_st

                    #NO SABEMOS SI: el neto + garantia no puede superar la cota de garantia.
                    #total = min(valor_minimo, salario_neto+valor)
                    #NOtar que sigo usando la variable 'total' Por si es necesario usar la linea anterior
                    #borramos la de abajo y listo.
                    
                    total = valor
                    garantia = total - salario_neto

                    rem_obj = RemuneracionFija(
                        codigo=garantia_code,
                        nombre= garantia_name + ' (' + unicode(garantia_obj) + ')',
                        aplicacion='U', valor=garantia
                    )
                    rem_list.append( (rem_obj, garantia) )
                    acum_rem += garantia
                    salario_neto += garantia


        # Aqui iran los resultados del calculo para este cargo en particular.
        form_res = {
            'cargo': cargo_obj,
            'basico': basico.valor,
            'retenciones': ret_list,
            'remuneraciones': rem_list,
            'acum_ret': acum_ret,
            'acum_rem': acum_rem,
            'salario_bruto': salario_bruto,
            'salario_neto': salario_neto,
            'antiguedad': antiguedad,
            'antiguedad_importe': antiguedad_importe
        }
        form_res.update(daspu_context)
        lista_res.append(form_res)

        # Calculo los acumulados de los salarios para todos los cargos univs.
        # y tambien los acumulados de las remuneraciones y retenciones.
        total_rem += acum_rem
        total_ret += acum_ret
        total_bruto += salario_bruto
        total_neto += salario_neto

    context['total_rem'] = total_rem
    context['total_ret'] = total_ret
    context['total_bruto'] = total_bruto
    context['total_neto'] = total_neto
    context['lista_res'] = lista_res


    return context



def processPreUnivFormSet(commonform, preunivformset):
    """Procesa un formset con formularios de cargos preuniversitarios.
    Retorna un context."""

    antiguedad = commonform.cleaned_data['antiguedad']
    fecha = commonform.cleaned_data['fecha']
    has_doctorado = commonform.cleaned_data['doctorado']
    has_master = commonform.cleaned_data['master']
    es_afiliado = commonform.cleaned_data['afiliado']
    context = {}

    #guardo en esta lista un diccionario para cada formulario procesado
    #en cada una de estas, los resultados para renderizar luego.
    lista_res = list()

    # Itero sobre todos los cargos.
    total_rem = 0.0
    total_ret = 0.0
    total_bruto = 0.0
    total_neto = 0.0

    # Obtengo las Retenciones / Remuneraciones que son para cargos preuniversitarios.
    ret_rem_cargo_preuniv = get_retenciones_remuneraciones('P', 'C', fecha)
    ret_rem_cargo_all = get_retenciones_remuneraciones('T', 'C', fecha)
    ret_porcentuales = ret_rem_cargo_preuniv['ret_porcentuales'] | ret_rem_cargo_all['ret_porcentuales']
    ret_fijas = ret_rem_cargo_preuniv['ret_fijas'] | ret_rem_cargo_all['ret_fijas']
    rem_porcentuales = ret_rem_cargo_preuniv['rem_porcentuales'] | ret_rem_cargo_all['rem_porcentuales']
    rem_fijas = ret_rem_cargo_preuniv['rem_fijas'] | ret_rem_cargo_all['rem_fijas']

    # Obtengo la Antiguedad
    antiguedades = AntiguedadPreUniversitaria.objects.filter(
        anio=antiguedad,
        vigencia_desde__lte=fecha,
        vigencia_hasta__gte=fecha
    )
    antiguedad = None
    if not antiguedades.exists():
        context['error_msg'] = u'No existe información de Antigüedad para los datos ingresados. Por favor introduzca otros datos.'
        return context
    else:
        antiguedad = antiguedades.order_by('vigencia_hasta')[antiguedades.count()-1]
        for ant in antiguedades:
            rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = ant.remuneracion.codigo)


    for preunivform in preunivformset:

        if preunivform in preunivformset.deleted_forms:
            continue
        
        cargo_obj = preunivform.cleaned_data['cargo']
        horas = preunivform.cleaned_data['horas']


        ###### Salario Bruto.
        basicos = SalarioBasico.objects.filter(cargo=cargo_obj, vigencia_desde__lte=fecha, vigencia_hasta__gte=fecha)
        basico = None
        antiguedad_importe = 0.0
        salario_bruto = 0.0
        if not basicos.exists():
            context['error_msg'] = u'No existe información de Salarios Básicos para los datos ingresados. Por favor introduzca otros datos.'
            return context
        else:
            basico = basicos.order_by('vigencia_hasta')[basicos.count()-1]
            for bas in basicos:
                rem_fijas = rem_fijas.exclude(remuneracion__codigo = bas.remuneracion.codigo)


        if cargo_obj.pago_por_hora:
            antiguedad_importe = basico.valor * horas * antiguedad.porcentaje / 100.0
            salario_bruto = basico.valor * horas + antiguedad_importe
        else:
            antiguedad_importe = basico.valor * antiguedad.porcentaje / 100.0
            salario_bruto = basico.valor + antiguedad_importe


        ###### El Neto se calcula del bruto restando las retenciones y sumando las remuneraciones.

        ret_list = list()   # Aqui iran tuplas de la forma (obj retencion, importe) para mostrar esta info en el template
        rem_list = list()  # De forma similar, va a tener tuplas (obj remuneracion, importe)

        acum_ret = 0.   # El acumulado de todo lo que hay que descontarle al bruto.
        acum_rem = 0. # El acumulado de todo lo que hay que sumarle.


        ## Remuneraciones Especiales:        

        # Adicional titulo doctorado nivel medio (cod 53), Adicional titulo maestria nivel medio (cod 55)
        rem_porcentuales = filter_doc_masters_from_rem_porcentuales(rem_porcentuales, has_doctorado, has_master, 'P')

        # FONID.
        rem_fijas_cargo = RemuneracionFijaCargo.objects.filter(
            cargo=cargo_obj,
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha
        )
        if rem_fijas_cargo.exists():
            for rem in rem_fijas_cargo:
                if cargo_obj.pago_por_hora:
                    acum_rem += min(rem.valor * horas, 430.0)
                    rem_list.append( (rem, min(rem.valor * horas, 430.0)) )
                else:
                    acum_rem += min(rem.valor, 430.0)
                    rem_list.append( (rem, min(rem.valor, 430.0)) )
                rem_fijas = rem_fijas.exclude(remuneracion=rem.remuneracion)
        else:
            for rem in RemuneracionFijaCargo.objects.all():
                rem_fijas = rem_fijas.exclude(remuneracion=rem.remuneracion)


        ## Retenciones NO especiales:
        if not es_afiliado:
            ret_porcentuales = ret_porcentuales.exclude(retencion__codigo = afiliacion_code)

        for ret in ret_porcentuales:
                importe = salario_bruto * ret.porcentaje / 100.
                acum_ret = acum_ret + importe
                ret_list.append( (ret, importe) )

        for ret in ret_fijas:
                acum_ret = acum_ret + ret.valor
                ret_list.append( (ret, ret.valor) )

        for rem in rem_porcentuales:
                importe = salario_bruto * rem.porcentaje / 100.
                acum_rem = acum_rem + importe
                rem_list.append( (rem, importe) )

        for rem in rem_fijas:
                acum_rem = acum_rem + rem.valor
                rem_list.append( (rem, rem.valor) )
            

        ###### Salario Neto.
        salario_neto = salario_bruto - acum_ret + acum_rem

        ## Garantia salarial.
        garantias_salariales = GarantiaSalarialPreUniversitaria.objects.filter(
            cargo=cargo_obj,
            vigencia_desde__lte=fecha,
            vigencia_hasta__gte=fecha
        )

        if garantias_salariales.exists():

            garantia_obj = garantia_salarial_objs.order_by('vigencia_hasta')[garantia_salarial_objs.count()-1]
            valor_minimo = garantia_obj.valor_minimo

            if salario_neto < valor_minimo:

                garantia = valor_minimo - salario_neto

                rem_obj = RemuneracionFija(
                    codigo=garantia_code,
                    nombre= garantia_name + ' (' + unicode(garantia_obj) + ')',
                    aplicacion='U',
                    valor=garantia
                )
                rem_list.append( (rem_obj, garantia) )
                acum_rem += garantia
                salario_neto += garantia


        # Aqui iran los resultados del calculo para este cargo en particular.
        form_res = {
            'cargo': cargo_obj,
            'basico_horas': basico.valor * horas,
            'basico': basico.valor,
            'retenciones': ret_list,
            'remuneraciones': rem_list,
            'acum_ret': acum_ret,
            'acum_rem': acum_rem,
            'salario_bruto': salario_bruto,
            'salario_neto': salario_neto,
            'antiguedad': antiguedad,
            'antiguedad_importe': antiguedad_importe
        }
        lista_res.append(form_res)

        print form_res

        # Calculo los acumulados de los salarios para todos los cargos.
        # y tambien los acumulados de las remuneraciones y retenciones.
        total_rem += acum_rem
        total_ret += acum_ret
        total_bruto += salario_bruto
        total_neto += salario_neto


    context['total_rem'] = total_rem
    context['total_ret'] = total_ret
    context['total_bruto'] = total_bruto
    context['total_neto'] = total_neto
    context['lista_res'] = lista_res

    return context
