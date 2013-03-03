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

import datetime

# Debugger
import pdb

###############################################
# Hardcoded
###############################################

doc_code = '05/1'
doc_preuniv_code = '05/3'

master_code = '05/2'
master_preuniv_code = '05/5'

garantia_code = '11/5'
garantia_name = u'Garantía Docentes Univ.'

garantia_preuniv_code = '10/7'
garantia_preuniv_name = u'Garantía Nivel Medio'

adic_118_code = '11/8'
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
            total_no_rem = add_values_from_contexts(context_univ, context_preuniv, 'total_no_rem')
            total_ret = add_values_from_contexts(context_univ, context_preuniv, 'total_ret')
            total_neto = add_values_from_contexts(context_univ, context_preuniv, 'total_neto')

            fecha = datetime.date(int(commonform.cleaned_data['anio']), int(commonform.cleaned_data['mes']), 10)
            # Hago el merge de los dos contexts.
            context['total_rem'] = total_rem
            context['total_no_rem'] = total_no_rem
            context['total_ret'] = total_ret
            context['total_neto'] = total_neto
            context['fecha'] = fecha

            context['lista_res'] = list()
            if context_univ.has_key('lista_res'):
                context['lista_res'].extend(context_univ['lista_res'])
                nro_forms_univ = len(context_univ['lista_res'])
            if context_preuniv.has_key('lista_res'):
                context['lista_res'].extend(context_preuniv['lista_res'])
                nro_forms_preuniv = len(context_preuniv['lista_res'])

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
                conf,
                nro_forms_univ,
                nro_forms_preuniv
                )
            #### Usando el neto, chequeo si hacen falta aplicar garantias salariales.
            #context = calculateGarantiasSalariales(context, context_univ['codigos_cargo'], context_preuniv['lista_res'], fecha)
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

#def calculateGarantiasSalariales(context, codigos_univ, context_preuniv, fecha):
    #""" Si hay que aplicar garantías salariales se modifica el contexto,
        #sino queda todo igual."""

    #gar_univ = GarantiaSalarialUniversitaria.objects.filter(vigencia__desde__lte=fecha, vigencia__hasta__gte=fecha)
    ##gar_preuniv = GarantiaSalarialPreUniversitaria.objects.filter(vigencia__desde__lte=fecha, vigencia__hasta__gte=fecha)
    #if len(codigos_univ) == 1:
        #codigo = codigos_univ[0]
        #for gu in gar_univ:
            #if codigo in map(lambda x: x['pampa'], gu.cargo.values()):
                # Aplicar la garantía.
                
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
            vigencia__desde__lte=fecha,
            vigencia__hasta__gte=fecha
        )

        # De todas las anteriores tomo la de fecha vigente.
        if afamiliares:
            afamiliar = afamiliares.order_by('vigencia__hasta')[afamiliares.count()-1]
            afamiliares_list.append(afamiliar)
            total += afamiliar.valor

    return (afamiliares_list,total)


def processDetailsForm(context, detailsform, ret_fija_persona, acum_ret):

    fecha = context['fecha']
    
    sis = detailsform.cleaned_data['sis']
    sf = detailsform.cleaned_data['subsidio_fallecimiento']
    fs_mayores = detailsform.cleaned_data['fondo_solidario_mayores']
    fs_menores = detailsform.cleaned_data['fondo_solidario_menores']
    
    #result = {}

    #en principio estos datos son retenciones por persona
    #los datos se guardan indicando esa categoria para luego ser procesados en..  (ej: l656+ ) 

    if fs_mayores > 0.0:
        fs_objs= FondoSolidario.objects.filter(
            retencion__codigo=fs_code,
            vigencia__desde__lte=fecha,
            vigencia__hasta__gte=fecha,
            concepto='Fondo solidario para una persona (mayor a 55 años)'
            )
        if not fs_objs.exists():
            result["error_msg"] = "No hay información sobre Fondo solidario para personas mayores de 55 años."
        else:
            fs_obj = fs_objs.order_by('vigencia__hasta')[fs_objs.count()-1]
            importe = fs_obj.valor * fs_mayores
            #result['fs_mayores'] = ('retencion_fija_persona',fs_obj,importe)
            acum_ret += importe
            ret_fija_persona.append((fs_obj, importe))

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
                vigencia__desde__lte=fecha,
                vigencia__hasta__gte=fecha,
                concepto=query
            )
        if not fs_objs.exists():
            result["error_msg"] = "No hay información sobre Fondo solidario"
        else:
            fs_obj = fs_objs.order_by('vigencia__hasta')[fs_objs.count()-1]
            importe = fs_obj.valor
            #result['fs_menores'] = ('retencion_fija_persona',fs_obj,importe)
            acum_ret += importe
            ret_fija_persona.append((fs_obj, importe))

    if sis:    
        sis_objs= RetencionFija.objects.filter(
                retencion__codigo=sis_code,
                vigencia__desde__lte=fecha,
                vigencia__hasta__gte=fecha
            )
        if not sis_objs.exists():
            result["error_msg"] = "No existe informacion sobre Seguro Integral de Sepelio."
        else:
            sis_obj = sis_objs.order_by('vigencia__hasta')[sis_objs.count()-1]
            #result['sis'] = ('retencion_fija_persona',sis_obj,sis_obj.valor)
            acum_ret += sis_obj.valor
            ret_fija_persona.append((sis_obj, sis_obj.valor))

    if sf:    
        sf_objs= RetencionFija.objects.filter(
                retencion__codigo=subsidio_fallecimiento_code,
                vigencia__desde__lte=fecha,
                vigencia__hasta__gte=fecha
            )
        if not sf_objs.exists():
            result["error_msg"] = "No existe informacion sobre Subsidio por Fallecimiento."
        else:
            sf_obj = sf_objs.order_by('vigencia__hasta')[sf_objs.count()-1]
            #result['sf'] = ('retencion_fija_persona',sf_obj,sf_obj.valor)
            acum_ret += sf_obj.valor
            ret_fija_persona.append((sf_obj, sf_obj.valor))

    return ret_fija_persona, acum_ret

def calculateDASPU(fecha,remunerativo):
    
    daspu_context={}
    daspu_importe = 0.0
    daspu_extra = 0.0

    rets_porc_daspu = RetencionPorcentual.objects.filter(
        retencion__codigo =daspu_code,
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
        )
    if rets_porc_daspu.exists():
        r = rets_porc_daspu.order_by('vigencia__hasta')[rets_porc_daspu.count()-1]

        daspu_objs = RetencionDaspu.objects.filter(
            retencion=r,
            )
        if not daspu_objs.exists():
            context["error_msg"] = "No existe informacion sobre afiliaciones para DASPU.\n"
        else:
            daspu_obj = daspu_objs[daspu_objs.count()-1]
            p = daspu_obj.retencion.porcentaje # 3%
            p_min = daspu_obj.porcentaje_minimo # 8%

            # Corroborar si no cubre el minimo de del cargo ayudante D.S.E. sin antiguedad.
            basicos = SalarioBasicoUniv.objects.filter(
                cargo=daspu_obj.cargo_referencia,
                vigencia__desde__lte=fecha,
                vigencia__hasta__gte=fecha
                )
            if not basicos.exists():
                context['error_msg']='No se encuentra la información salarial requerida para el cálculo.'
            else:
                basico = basicos.order_by('vigencia__hasta')[basicos.count()-1]
                basico = basico.valor
                daspu_importe += remunerativo * p / 100.0
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
afamiliaresformset, afamiliaresformespecial, detailsform, gananciasform, conf,
nro_forms_univ, nro_forms_preuniv):

    fecha = context['fecha']
    total_rem = context['total_rem']
    total_no_rem = context['total_no_rem']
    total_ret = context['total_ret']
    total_neto = context['total_neto']

    # Retenciones / Remuneraciones que son por persona para todos los cargos.
    pers_all = get_retenciones_remuneraciones('T', 'P', fecha)
    ret_fp = pers_all['ret_fijas']
    ret_pp = pers_all['ret_porcentuales']
    rem_fp = pers_all['rem_fijas']
    rem_pp = pers_all['rem_porcentuales']

    if nro_forms_univ > 0:
        # Retenciones / Remuneraciones que son por persona para cargos Universitarios.
        pers_univ = get_retenciones_remuneraciones('U', 'P', fecha)
        ret_fp = ret_fp | pers_univ['ret_fijas']
        ret_pp = ret_pp | pers_univ['ret_porcentuales']
        rem_fp = rem_fp | pers_univ['rem_fijas']
        rem_pp = rem_pp | pers_univ['rem_porcentuales']

    if nro_forms_preuniv > 0:
        # Retenciones / Remuneraciones que son por persona para cargos Preuniversitarios.
        pers_preuniv = get_retenciones_remuneraciones('P', 'P', fecha)
        ret_fp = ret_fp | pers_preuniv['ret_fijas']
        ret_pp = ret_pp | pers_preuniv['ret_porcentuales']
        rem_fp = rem_fp | pers_preuniv['rem_fijas']
        rem_pp = rem_pp | pers_preuniv['rem_porcentuales']

    # Calculo las retenciones/remuneraciones que son por persona.
    acum_ret = 0.0
    acum_rem = 0.0

    ret_porc_persona = list()
    rem_porc_persona = list()
    ret_fijas_persona = list()
    rem_fijas_persona = list()

    # Proceso el formulario de asignacion familiar.

    #afamiliares_list, total_afamiliares = processAFamiliaresFormSet(context, afamiliaresformset, afamiliaresformespecial, conf)

    #acum_rem += total_afamiliares

    # Saco las DAS de ret_fp y proceso el formulario de daspu.
    ret_fp = ret_fp.exclude(retencion__codigo__startswith='DAS')
    ret_fijas_persona, acum_ret = processDetailsForm(context, detailsform, ret_fijas_persona, acum_ret)

    for ret in ret_pp:
        importe = (total_rem * ret.porcentaje / 100.0)
        acum_ret += importe
        ret_porc_persona.append( (ret, importe) )

    for ret in ret_fp:
        acum_ret += ret.valor
        ret_fijas_persona.append( (ret, ret.valor) )

    for rem in rem_pp:
        importe = (total_rem * ret.porcentaje / 100.0)
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
            vigencia__desde__lte=fecha,
            vigencia__hasta__gte=fecha
        )
        if deducciones_objs.exists():
            deducciones_obj = deducciones_objs.order_by('vigencia__hasta')[deducciones_objs.count()-1]
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
            vigencia__desde__lte=fecha,
            vigencia__hasta__gte=fecha
        )
        if ganancias_tablas.exists():
            ganancias_tabla = ganancias_tablas.order_by('vigencia__hasta')[ganancias_tablas.count()-1]
            importe_ganancias = ganancias_tabla.impuesto_fijo + (ganancia_neta - ganancias_tabla.sobre_exedente_de) * (ganancias_tabla.impuesto_porcentual / 100)

        ganancias_retencion_objs = Retencion.objects.filter(codigo='42/0')
        if importe_ganancias >= 0 and ganancias_retencion_objs.exists():
            new_ret_fija = RetencionFija(retencion=ganancias_retencion_objs[0], valor=importe_ganancias / 12, vigencia__desde=fecha, vigencia__hasta=fecha)
            ret_fijas_persona.append( (new_ret_fija, new_ret_fija.valor) )
            acum_ret += importe_ganancias / 12



    total_ret += acum_ret
    total_rem += acum_rem

    total_neto = total_neto - acum_ret + acum_rem

    context['ret_fijas_persona'] = ret_fijas_persona
    context['ret_porc_persona'] = ret_porc_persona
    context['rem_fijas_persona'] = rem_fijas_persona
    context['rem_porc_persona'] = rem_porc_persona
    #context['afamiliares_list'] = afamiliares_list

    #context['total_bruto'] = total_bruto
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
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
    )
    ret_porcentuales = RetencionPorcentual.objects.filter(
        retencion__aplicacion=aplicacion,
        retencion__modo=modo,
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
    )
    rem_fijas = RemuneracionFija.objects.filter(
        remuneracion__aplicacion=aplicacion,
        remuneracion__modo=modo,
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
    )
    rem_porcentuales  = RemuneracionPorcentual.objects.filter(
        remuneracion__aplicacion=aplicacion,
        remuneracion__modo=modo,
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
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
    #fecha = commonform.cleaned_data['fecha']
    fecha = datetime.date(int(commonform.cleaned_data['anio']), int(commonform.cleaned_data['mes']), 10)
    has_doctorado = commonform.cleaned_data['doctorado']
    has_master = commonform.cleaned_data['master']
    #afiliacion adiuc:
    es_afiliado = commonform.cleaned_data['afiliado']

    context = {}

    #Guardo en esta lista un diccionario para cada formulario procesado
    lista_res = list()
    #codigos_cargo = list()

    total_rem = 0.0
    total_no_rem = 0.0
    total_ret = 0.0
    total_neto = 0.0

    # Obtengo las Retenciones / Remuneraciones que son para cargos universitarios.
    ret_rem_cargo_univ = get_retenciones_remuneraciones('U', 'C', fecha)
    ret_rem_cargo_all = get_retenciones_remuneraciones('T', 'C', fecha)
    # El operador | es la union de qs. & es la interseccion.
    ret_fijas = ret_rem_cargo_univ['ret_fijas'] | ret_rem_cargo_all['ret_fijas'] 
    ret_porcentuales = ret_rem_cargo_univ['ret_porcentuales'] | ret_rem_cargo_all['ret_porcentuales']
    rem_fijas = ret_rem_cargo_univ['rem_fijas'] | ret_rem_cargo_all['rem_fijas']
    rem_porcentuales = ret_rem_cargo_univ['rem_porcentuales'] | ret_rem_cargo_all['rem_porcentuales']

    # Obtengo la Antiguedad
    antiguedades = AntiguedadUniversitaria.objects.filter(
        anio=antiguedad,
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
    )
    antiguedad = None
    if not antiguedades.exists():
        context['error_msg'] = u'No existe información de Salarios Básicos \
        para los datos ingresados. Por favor intente con otros datos.'
        return context
    else:
        antiguedad = antiguedades.order_by('vigencia__hasta')[antiguedades.count()-1]
        for ant in antiguedades:
            rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = ant.remuneracion.codigo)

    for univform in univformset:

        # No analizamos los forms que fueron borrados por el usuario.
        if univform in univformset.deleted_forms:
            continue

        cargo_obj = univform.cleaned_data['cargo']

        ###### Salario Bruto.
        # Registro el bonificable, el remunerativo, el no remunerativo y los descuentos.
        bonificable = 0.0
        remunerativo = 0.0
        no_remunerativo = 0.0
        descuentos = 0.0
        ret_list = list()  # Tuplas de la forma (obj retencion, importe).
        rem_list = list()  # Tuplas (obj remuneracion, importe).

        # El basico fijado en septiembre del año anterior.
        basicos = SalarioBasicoUniv.objects.filter(
                    cargo=cargo_obj,
                    vigencia__desde__lte=fecha,
                    vigencia__hasta__gte=fecha
                  )
        basico = None
        if not basicos.exists():
            context['error_msg'] = u'No existe información de Salarios Básicos \
            para los datos ingresados. Por favor intente con otros datos.'
            return context
        else:
            basico = basicos.order_by('vigencia__hasta')[basicos.count()-1]
            bonificable += basico.valor # Sumo el basico al bonificable.
            remunerativo += basico.valor
            rem_fijas = rem_fijas.exclude(remuneracion__codigo = basico.remuneracion.codigo)

        # Obtengo las remunaraciones fijas inherentes al cargo que sean bonificables.
        rems_fijas_cargo = RemuneracionFijaCargo.objects.filter(
                            cargo = cargo_obj,
                            vigencia__desde__lte=fecha,
                            vigencia__hasta__gte=fecha,
                            remuneracion__bonificable=True
                          )
        if rems_fijas_cargo.exists():
            for rem in rems_fijas_cargo:
                # Sumo el bonificable, el remunerativo y el no remunerativo segun corresponda.
                bonificable += rem.valor
                remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0

                rem_fijas = rem_fijas.exclude(remuneracion__codigo = rem.remuneracion.codigo)
                rem_list.append( (rem, rem.valor) )

        # Obtengo las otras remuneraciones fijas bonificables.
        rems_fijas_otras = RemuneracionFija.objects.filter(
                                vigencia__desde__lte=fecha,
                                vigencia__hasta__gte=fecha,
                                remuneracion__bonificable=True,
                                remuneracionfijacargo=None,
                                salariobasicouniv=None,
                                salariobasicopreuniv=None
                           )
        if rems_fijas_otras.exists():
            # Sumo el bonificable, el remunerativo y el no remunerativo segun corresponda.
            for rem in rems_fijas_otras:
                bonificable += rem.valor
                remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0

                rem_fijas = rem_fijas.exclude(remuneracion__codigo = rem.remuneracion.codigo)
                rem_list.append( (rem, rem.valor) )

        # Obtengo los nomencladores.
        rems_nomenclador = RemuneracionNomenclador.objects.filter(
                                vigencia__desde__lte=fecha,
                                vigencia__hasta__gte=fecha,
                                remuneracion__bonificable=True,
                                cargo = cargo_obj
                            )
        adic_nom = 0.0
        if rems_nomenclador.exists():
            adic_nom = rems_nomenclador[0].porcentaje
        rem_porcentuales = rem_porcentuales.exclude(remuneracionnomenclador__isnull=False)
        # Obtengo las remuneraciones porcentuales bonificables.
        rems_porc_bonif = RemuneracionPorcentual.objects.filter(
                            vigencia__desde__lte=fecha,
                            vigencia__hasta__gte=fecha,
                            remuneracion__bonificable=True,
                            remuneracionnomenclador=None
                          )
        if rems_porc_bonif.exists():
            for rem in rems_porc_bonif:
                porcentaje = rem.porcentaje + adic_nom if rem.nomenclador else rem.porcentaje
                if rem.sobre_referencia:
                    # Sumo el porcentaje por el salario referencia.
                    importe = basico.salario_referencia * porcentaje / 100.0
                else:
                    importe = basico.valor * porcentaje / 100.0
                bonificable += importe
                remunerativo += importe if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += importe if not rem.remuneracion.remunerativo else 0.0
                if importe > 0.0:
                    rem_list.append( (rem, importe) )
                rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = rem.remuneracion.codigo)
        antiguedad_importe = bonificable * antiguedad.porcentaje / 100.0
        remunerativo += antiguedad_importe

        # Adicional titulo doctorado (cod 51), Adicional titulo maestria (cod 52)
        rem_porcentuales = filter_doc_masters_from_rem_porcentuales(rem_porcentuales, has_doctorado, has_master, 'U')

        if not es_afiliado:
            ret_porcentuales = ret_porcentuales.exclude(retencion__codigo = afiliacion_code)

        ## Retenciones / Remuneraciones NO especiales:
        for rem in rem_porcentuales:
            importe = bonificable * rem.porcentaje / 100.
            remunerativo += importe if rem.remuneracion.remunerativo else 0.0
            no_remunerativo += importe if not rem.remuneracion.remunerativo else 0.0
            rem_list.append( (rem, importe) )

        for rem in rem_fijas:
            remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
            no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0
            rem_list.append( (rem, rem.valor) )

        for ret in ret_porcentuales:
            importe = remunerativo * ret.porcentaje / 100.
            descuentos += importe
            ret_list.append( (ret, importe) )

        for ret in ret_fijas:
            descuentos += ret.valor
            ret_list.append( (ret, ret.valor) )

        # Calculo afiliacion daspu
        #daspu_context = calculateDASPU(fecha,remunerativo)
        #if daspu_context.has_key('error_msg'):
            #context['error_msg'] = "\n"+daspu_context['error_msg']

        #daspu_importe = daspu_context['daspu_importe']
        #descuentos += daspu_importe

        ###### Salario Neto.
        salario_neto = remunerativo + no_remunerativo - descuentos

        # Aqui iran los resultados del calculo para este cargo en particular.
        form_res = {
            'cargo': cargo_obj,
            'basico': basico.valor,
            'retenciones': ret_list,
            'remuneraciones': rem_list,
            'descuentos': descuentos,
            'remunerativo': remunerativo,
            'no_remunerativo': no_remunerativo,
            'salario_neto': salario_neto,
            'antiguedad': antiguedad,
            'antiguedad_importe': antiguedad_importe,
        }
        #form_res.update(daspu_context)
        lista_res.append(form_res)
        #codigos_cargo.append(cargo_obj.pampa)

        # Calculo los acumulados de los salarios para todos los cargos univs.
        # y tambien los acumulados de las remuneraciones y retenciones.
        total_rem += remunerativo
        total_no_rem += no_remunerativo
        total_ret += descuentos
        total_neto += salario_neto

    context['total_rem'] = total_rem
    context['total_no_rem'] = total_no_rem
    context['total_ret'] = total_ret
    context['total_neto'] = total_neto
    context['lista_res'] = lista_res
    #context['codigos_cargo'] = codigos_cargo


    return context



def processPreUnivFormSet(commonform, preunivformset):
    """Procesa un formset con formularios de cargos preuniversitarios.
    Retorna un context."""

    antiguedad = commonform.cleaned_data['antiguedad']
    #fecha = commonform.cleaned_data['fecha']
    fecha = datetime.date(int(commonform.cleaned_data['anio']), int(commonform.cleaned_data['mes']), 10)
    has_doctorado = commonform.cleaned_data['doctorado']
    has_master = commonform.cleaned_data['master']
    es_afiliado = commonform.cleaned_data['afiliado']
    context = {}

    #guardo en esta lista un diccionario para cada formulario procesado
    #en cada una de estas, los resultados para renderizar luego.
    lista_res = list()

    # Itero sobre todos los cargos.
    total_rem = 0.0
    total_no_rem = 0.0
    total_ret = 0.0
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
        vigencia__desde__lte=fecha,
        vigencia__hasta__gte=fecha
    )
    antiguedad = None
    if not antiguedades.exists():
        context['error_msg'] = u'No existe información de Antigüedad para los datos ingresados. Por favor introduzca otros datos.'
        return context
    else:
        antiguedad = antiguedades.order_by('vigencia__hasta')[antiguedades.count()-1]
        for ant in antiguedades:
            rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = ant.remuneracion.codigo)


    for preunivform in preunivformset:

        if preunivform in preunivformset.deleted_forms:
            continue
        
        cargo_obj = preunivform.cleaned_data['cargo']
        horas = preunivform.cleaned_data['horas']


        ###### Salario Bruto.
        # Registro el bonificable, el remunerativo, el no remunerativo y los descuentos.
        bonificable = 0.0
        remunerativo = 0.0
        no_remunerativo = 0.0
        descuentos = 0.0
        ret_list = list()  # Tuplas de la forma (obj retencion, importe).
        rem_list = list()  # Tuplas (obj remuneracion, importe).

        # El basico fijado en septiembre del año anterior.
        basicos = SalarioBasicoPreUniv.objects.filter(
                    cargo=cargo_obj,
                    vigencia__desde__lte=fecha,
                    vigencia__hasta__gte=fecha
                  )
        basico = None
        antiguedad_importe = 0.0
        salario_bruto = 0.0
        if not basicos.exists():
            context['error_msg'] = u'No existe información de Salarios Básicos para los datos ingresados. Por favor introduzca otros datos.'
            return context
        else:
            basico = basicos.order_by('vigencia__hasta')[basicos.count()-1]
            for bas in basicos:
                rem_fijas = rem_fijas.exclude(remuneracion__codigo = bas.remuneracion.codigo)

        # Sumo el basico al bonificable.
        bonificable += basico.valor * horas if cargo_obj.pago_por_hora else basico.valor
        remunerativo += basico.valor * horas if cargo_obj.pago_por_hora else basico.valor
        
        # Obtengo las remunaraciones fijas inherentes al cargo que sean bonificables.
        rems_fijas_cargo = RemuneracionFijaCargo.objects.filter(
                            cargo = cargo_obj,
                            vigencia__desde__lte=fecha,
                            vigencia__hasta__gte=fecha,
                            remuneracion__bonificable=True
                          )
        if rems_fijas_cargo.exists():
            for rem in rems_fijas_cargo:
                # Sumo el bonificable, el remunerativo y el no remunerativo segun corresponda.
                bonificable += rem.valor
                remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0

                rem_fijas = rem_fijas.exclude(remuneracion__codigo = rem.remuneracion.codigo)
                rem_list.append( (rem, rem.valor) )

        # Obtengo las otras remuneraciones fijas bonificables.
        rems_fijas_otras = RemuneracionFija.objects.filter(
                                vigencia__desde__lte=fecha,
                                vigencia__hasta__gte=fecha,
                                remuneracion__bonificable=True,
                                remuneracionfijacargo=None,
                                salariobasicouniv=None,
                                salariobasicopreuniv=None
                           )
        if rems_fijas_otras.exists():
            # Sumo el bonificable, el remunerativo y el no remunerativo segun corresponda.
            for rem in rems_fijas_otras:
                bonificable += rem.valor
                remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0

                rem_fijas = rem_fijas.exclude(remuneracion__codigo = rem.remuneracion.codigo)
                rem_list.append( (rem, rem.valor) )

        # Obtengo los nomencladores.
        rems_nomenclador = RemuneracionNomenclador.objects.filter(
                                vigencia__desde__lte=fecha,
                                vigencia__hasta__gte=fecha,
                                remuneracion__bonificable=True,
                                cargo = cargo_obj
                            )
        adic_nom = 0.0
        if rems_nomenclador.exists():
            adic_nom = rems_nomenclador[0].porcentaje
        rem_porcentuales = rem_porcentuales.exclude(remuneracionnomenclador__isnull=False)
        # Obtengo las remuneraciones porcentuales bonificables.
        rems_porc_bonif = RemuneracionPorcentual.objects.filter(
                            vigencia__desde__lte=fecha,
                            vigencia__hasta__gte=fecha,
                            remuneracion__bonificable=True,
                            remuneracionnomenclador=None
                          )
        if rems_porc_bonif.exists():
            for rem in rems_porc_bonif:
                porcentaje = rem.porcentaje + adic_nom if rem.nomenclador else rem.porcentaje
                importe = basico.valor * horas * porcentaje / 100.0 if cargo_obj.pago_por_hora else basico.valor * porcentaje/100.0
                bonificable += importe
                remunerativo += importe if rem.remuneracion.remunerativo else 0.0
                no_remunerativo += importe if not rem.remuneracion.remunerativo else 0.0
                if importe > 0.0:
                    rem_list.append( (rem, importe) )
                rem_porcentuales = rem_porcentuales.exclude(remuneracion__codigo = rem.remuneracion.codigo)
        antiguedad_importe = bonificable * antiguedad.porcentaje / 100.0
        remunerativo += antiguedad_importe        

        # Adicional titulo doctorado nivel medio (cod 53), Adicional titulo maestria nivel medio (cod 55)
        rem_porcentuales = filter_doc_masters_from_rem_porcentuales(rem_porcentuales, has_doctorado, has_master, 'P')

        # FONID.
        #rem_fijas_cargo = RemuneracionFijaCargo.objects.filter(
            #cargo=cargo_obj,
            #vigencia__desde__lte=fecha,
            #vigencia__hasta__gte=fecha
        #)
        #if rem_fijas_cargo.exists():
            #for rem in rem_fijas_cargo:
                #if cargo_obj.pago_por_hora:
                    #acum_rem += min(rem.valor * horas, 430.0)
                    #rem_list.append( (rem, min(rem.valor * horas, 430.0)) )
                #else:
                    #acum_rem += min(rem.valor, 430.0)
                    #rem_list.append( (rem, min(rem.valor, 430.0)) )
                #rem_fijas = rem_fijas.exclude(remuneracion=rem.remuneracion)
        #else:
            #for rem in RemuneracionFijaCargo.objects.all():
                #rem_fijas = rem_fijas.exclude(remuneracion=rem.remuneracion)


        ## Retenciones NO especiales:
        if not es_afiliado:
            ret_porcentuales = ret_porcentuales.exclude(retencion__codigo = afiliacion_code)

        for rem in rem_porcentuales:
            importe = bonificable * rem.porcentaje / 100.
            remunerativo += importe if rem.remuneracion.remunerativo else 0.0
            no_remunerativo += importe if not rem.remuneracion.remunerativo else 0.0
            rem_list.append( (rem, importe) )

        for rem in rem_fijas:
            remunerativo += rem.valor if rem.remuneracion.remunerativo else 0.0
            no_remunerativo += rem.valor if not rem.remuneracion.remunerativo else 0.0
            rem_list.append( (rem, rem.valor) )

        for ret in ret_porcentuales:
            importe = remunerativo * ret.porcentaje / 100.
            descuentos += importe
            ret_list.append( (ret, importe) )

        for ret in ret_fijas:
            descuentos += ret.valor
            ret_list.append( (ret, ret.valor) )
            

        ###### Salario Neto.
        salario_neto = remunerativo + no_remunerativo - descuentos

        # Aqui iran los resultados del calculo para este cargo en particular.
        form_res = {
            'cargo': cargo_obj,
            'basico_horas': basico.valor * horas,
            'basico': basico.valor,
            'retenciones': ret_list,
            'remuneraciones': rem_list,
            'descuentos': descuentos,
            'remunerativo': remunerativo,
            'no_remunerativo': no_remunerativo,
            'salario_neto': salario_neto,
            'antiguedad': antiguedad,
            'antiguedad_importe': antiguedad_importe
        }
        lista_res.append(form_res)

        #print form_res

        # Calculo los acumulados de los salarios para todos los cargos.
        # y tambien los acumulados de las remuneraciones y retenciones.
        total_rem += remunerativo
        total_no_rem += no_remunerativo
        total_ret += descuentos
        total_neto += salario_neto

    context['total_rem'] = total_rem
    context['total_no_rem'] = total_no_rem
    context['total_ret'] = total_ret
    context['total_neto'] = total_neto
    context['lista_res'] = lista_res

    return context
