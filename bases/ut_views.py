# -*- encoding: utf-8 -*-
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
import os
import django
import django.conf as conf
from bases.models import BaseEmpresa
from bases.models import ClienteActivo, Parametros, TablaGeneral
from celula.settings import STATICFILES_DIRS
from seguridad.models import Empresa, Pais, Region, Comuna, CajasCompensacion, Salud, Afp, Bancos


@login_required
@csrf_exempt
def crearMigrate(request, baseId, is_ajax):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jab.settings")
    django.setup()

    la_base = BaseEmpresa.objects.get(ba_id=baseId)
    lst_log = []
    lista_err = []

    lst_log.append({'log': '-- armando conexión...'})

    nueva_base = {
        'ENGINE': conf.settings.DATABASES['default']['ENGINE'],
        'HOST': la_base.ba_host,
        'NAME': la_base.ba_name,
        'USER': la_base.ba_user,
        'PASSWORD': la_base.ba_password,
        'PORT': la_base.ba_port
    }
    conf.settings.DATABASES[la_base.ba_conexion] = nueva_base

    lst_log.append({'log': '-- conexión creada...'})
    lst_log.append({'log': '-- ejecutando migrate de tablas...'})

    call_command('migrate', noinput=True, database=la_base.ba_conexion)

    lst_log.append({'log': '-- tablas creada con éxito...'})

    try:
        ca = ClienteActivo.objects.using(la_base.ba_conexion).get(cac_id=la_base.ba_idclienteactivo)
    except:
        ca = ClienteActivo()

    ca.cac_activo = 'S'
    ca.save(using=la_base.ba_conexion)

    la_base.ba_creada = 'S'
    la_base.ba_idclienteactivo = ca.cac_id
    la_base.save()

    if is_ajax:

        html = {
            'lst_log': lst_log,
            'lista_err': lista_err,
            'cac_activo': ca.cac_activo,
        }
        response = json.dumps(html)
        return HttpResponse(response, content_type='application/json')
    else:
        return lst_log


# -------------------------------------
@login_required
@csrf_exempt
def armarEstructuraCarpetaEmpresa(request, baseId, is_ajax):
    """
    1- se crea el directorio con el nombre de la empresa
    2- se crea el directorio dentro del directorio de empresa para los documentos
    3- se crea el directorio dentro del directorio de empresa para los usuarios
    :param request:
    :param baseId:
    :param is_ajax:
    :return:

        Esto es para carpeta static

    """
    lst_log = []

    la_base = BaseEmpresa.objects.get(ba_id=baseId)
    ba_conexion = la_base.ba_conexion

    directorio_static = STATICFILES_DIRS[0] + "/" + ba_conexion
    directorio_documentos = directorio_static + "/documentos"
    directorio_usuarios = directorio_static + "/usuarios"

    try:
        os.stat(directorio_static)
    except:
        os.mkdir(directorio_static)

    try:
        os.stat(directorio_documentos)
    except:
        os.mkdir(directorio_documentos)

    try:
        os.stat(directorio_usuarios)
    except:
        os.mkdir(directorio_usuarios)

    directorio_template = STATICFILES_DIRS[1] + "/" + ba_conexion
    try:
        os.stat(directorio_template)
    except:
        os.mkdir(directorio_template)

    cActivo = ClienteActivo.objects.using(la_base.ba_name).get(cac_id=la_base.ba_idclienteactivo)
    cActivo.cac_rutadocumentos = directorio_documentos
    cActivo.cac_rutadstatic = directorio_static
    cActivo.cac_rutausuarios = directorio_usuarios
    cActivo.save(using=ba_conexion)

    lst_log.append({'text': 'Directorios guardado con éxito...'})

    if is_ajax:
        html = {
            'lst_log': lst_log,
        }
        response = json.dumps(html)
        return HttpResponse(response, content_type='application/json')
    else:
        return lst_log


# -------------------------------------
@login_required
@csrf_exempt
def armarParametrosGeneralesDelSistema(request, id_base):
    la_base = BaseEmpresa.objects.get(ba_id=id_base)
    ba_nombre = la_base.ba_conexion
    lst_log = []

    p = Pais.objects.using(ba_nombre).filter(pa_codigo=56)
    if not p.exists():
        pa = Pais()
        pa.pa_nombre = 'Chile'
        pa.pa_codigo = 56
        pa.save(using=ba_nombre)
        pais = pa

        lst_log.append({'text': '* País: {} Código área: {}'.format(pa.pa_nombre, pa.pa_codigo)})
        lst_log.append({'text': '-- LISTADO DE PAISES CREADO CON EXITO --'})
    else:
        lst_log.append({'text': '* El país {} ya existe'.format(p[0].pa_nombre)})
        pais = p[0]

    lst_log.append({'text': '-----------------------------'})
    lst_log.append({'text': '* Listando regiones... '})
    lst_log.append({'text': '* Listando comunas...'})
    lst_regiones = [{
        're_nombre': 'Tarapacá',
        're_numeroregion': 'I',
        're_numero': 1,
        'comunas': [
            {'com_nombre': 'Iquique'},
            {'com_nombre': 'Alto Hospicio'},
            {'com_nombre': 'Pozo Almonte'},
            {'com_nombre': 'Camiña'},
            {'com_nombre': 'Colchane'},
            {'com_nombre': 'Huara'},
            {'com_nombre': 'Pica'},
        ]
    }, {
        're_nombre': 'Antofagasta',
        're_numeroregion': 'II',
        're_numero': 2,
        'comunas': [
            {'com_nombre': 'Antofagasta'},
            {'com_nombre': 'Mejillones'},
            {'com_nombre': 'Sierra Gorda'},
            {'com_nombre': 'Taltal'},
            {'com_nombre': 'Calama'},
            {'com_nombre': 'Ollagüe'},
            {'com_nombre': 'San Pedro de Atacama'},
            {'com_nombre': 'Tocopilla'},
            {'com_nombre': 'María Elena'},

        ]
    }, {
        're_nombre': 'Atacama',
        're_numeroregion': 'III',
        're_numero': 3,
        'comunas': [
            {'com_nombre': 'Copiapó'},
            {'com_nombre': 'Caldera'},
            {'com_nombre': 'Tierra Amarilla'},
            {'com_nombre': 'Chañaral'},
            {'com_nombre': 'Diego de Almagro'},
            {'com_nombre': 'Vallenar'},
            {'com_nombre': 'Alto del Carmen'},
            {'com_nombre': 'Freirina'},
            {'com_nombre': 'Huasco'},

        ]
    }, {
        're_nombre': 'Coquimbo',
        're_numeroregion': 'IV',
        're_numero': 4,
        'comunas': [
            {'com_nombre': 'Huasco'},
            {'com_nombre': 'La Serena'},
            {'com_nombre': 'Coquimbo'},
            {'com_nombre': 'Andacollo'},
            {'com_nombre': 'La Higuera'},
            {'com_nombre': 'Paiguano'},
            {'com_nombre': 'Vicuña'},
            {'com_nombre': 'Illapel'},
            {'com_nombre': 'Canela'},
            {'com_nombre': 'Los Vilos'},
            {'com_nombre': 'Salamanca'},
            {'com_nombre': 'Ovalle'},
            {'com_nombre': 'Combarbalá'},
            {'com_nombre': 'Monte Patria'},
            {'com_nombre': 'Punitaqui'},
            {'com_nombre': 'Río Hurtado'},

        ]
    }, {
        're_nombre': 'Valparaiso',
        're_numeroregion': 'V',
        're_numero': 5,
        'comunas': [
            {'com_nombre': 'Río Hurtado'},
            {'com_nombre': 'Valparaíso'},
            {'com_nombre': 'Casablanca'},
            {'com_nombre': 'Concón'},
            {'com_nombre': 'Juan Fernández'},
            {'com_nombre': 'Puchuncaví'},
            {'com_nombre': 'Quilpué'},
            {'com_nombre': 'Quintero'},
            {'com_nombre': 'Villa Alemana'},
            {'com_nombre': 'Viña del Mar'},
            {'com_nombre': 'Isla de Pascua'},
            {'com_nombre': 'Los Andes'},
            {'com_nombre': 'Calle Larga'},
            {'com_nombre': 'Rinconada'},
            {'com_nombre': 'San Esteban'},
            {'com_nombre': 'La Ligua'},
            {'com_nombre': 'Cabildo'},
            {'com_nombre': 'Papudo'},
            {'com_nombre': 'Petorca'},
            {'com_nombre': 'Zapallar'},
            {'com_nombre': 'Quillota'},
            {'com_nombre': 'Calera'},
            {'com_nombre': 'Hijuelas'},
            {'com_nombre': 'La Cruz'},
            {'com_nombre': 'Limache'},
            {'com_nombre': 'Nogales'},
            {'com_nombre': 'Olmué'},
            {'com_nombre': 'San Antonio'},
            {'com_nombre': 'Algarrobo'},
            {'com_nombre': 'Cartagena'},
            {'com_nombre': 'El Quisco'},
            {'com_nombre': 'El Tabo'},
            {'com_nombre': 'Santo Domingo'},
            {'com_nombre': 'San Felipe'},
            {'com_nombre': 'Catemu'},
            {'com_nombre': 'Llaillay'},
            {'com_nombre': 'Panquehue'},
            {'com_nombre': 'Putaendo'},
            {'com_nombre': 'Santa María'},

        ]
    }, {
        're_nombre': 'Metropolitana de Santiago',
        're_numeroregion': 'RM',
        're_numero': 13,
        'comunas': [
            {'com_nombre': 'Santiago'},
            {'com_nombre': 'Cerrillos'},
            {'com_nombre': 'Cerro Navia'},
            {'com_nombre': 'Conchalí'},
            {'com_nombre': 'El Bosque'},
            {'com_nombre': 'Estación Central '},
            {'com_nombre': 'Huechuraba'},
            {'com_nombre': 'Independencia'},
            {'com_nombre': 'La Cisterna'},
            {'com_nombre': 'La Florida'},
            {'com_nombre': 'La Pintana'},
            {'com_nombre': 'La Granja'},
            {'com_nombre': 'La Reina'},
            {'com_nombre': 'Las Condes'},
            {'com_nombre': 'Lo Barnechea'},
            {'com_nombre': 'Lo Espejo'},
            {'com_nombre': 'Lo Prado'},
            {'com_nombre': 'Macul'},
            {'com_nombre': 'Maipú'},
            {'com_nombre': 'Ñuñoa'},
            {'com_nombre': 'Pedro Aguirre Cerda'},
            {'com_nombre': 'Peñalolén'},
            {'com_nombre': 'Providencia'},
            {'com_nombre': 'Pudahuel'},
            {'com_nombre': 'Quilicura'},
            {'com_nombre': 'Quinta Normal'},
            {'com_nombre': 'Recoleta'},
            {'com_nombre': 'Renca'},
            {'com_nombre': 'San Joaquín'},
            {'com_nombre': 'San Miguel'},
            {'com_nombre': 'San Ramón'},
            {'com_nombre': 'Vitacura'},
            {'com_nombre': 'Puente Alto'},
            {'com_nombre': 'Pirque'},
            {'com_nombre': 'San José de Maipo'},
            {'com_nombre': 'Colina'},
            {'com_nombre': 'Lampa'},
            {'com_nombre': 'Tiltil'},
            {'com_nombre': 'San Bernardo'},
            {'com_nombre': 'Buin'},
            {'com_nombre': 'Calera de Tango'},
            {'com_nombre': 'Paine'},
            {'com_nombre': 'Melipilla'},
            {'com_nombre': 'Alhué'},
            {'com_nombre': 'Curacaví'},
            {'com_nombre': 'María Pinto'},
            {'com_nombre': 'San Pedro'},
            {'com_nombre': 'Talagante'},
            {'com_nombre': 'El Monte'},
            {'com_nombre': 'Isla de Maipo'},
            {'com_nombre': 'Padre Hurtado'},
            {'com_nombre': 'Peñaflor'},

        ]
    }, {
        're_nombre': 'Libertador General Bernardo O\'Higgins',
        're_numeroregion': 'VI',
        're_numero': 6,
        'comunas': [
            {'com_nombre': 'Rancagua'},
            {'com_nombre': 'Codegua'},
            {'com_nombre': 'Coinco'},
            {'com_nombre': 'Coltauco'},
            {'com_nombre': 'Doñihue'},
            {'com_nombre': 'Graneros'},
            {'com_nombre': 'Las Cabras'},
            {'com_nombre': 'Machalí'},
            {'com_nombre': 'Malloa'},
            {'com_nombre': 'Mostazal'},
            {'com_nombre': 'Olivar'},
            {'com_nombre': 'Peumo'},
            {'com_nombre': 'Pichidegua'},
            {'com_nombre': 'Quinta de Tilcoco'},
            {'com_nombre': 'Rengo'},
            {'com_nombre': 'Requínoa'},
            {'com_nombre': 'San Vicente'},
            {'com_nombre': 'Pichilemu'},
            {'com_nombre': 'La Estrella'},
            {'com_nombre': 'Litueche'},
            {'com_nombre': 'Marchihue'},
            {'com_nombre': 'Navidad'},
            {'com_nombre': 'Paredones'},
            {'com_nombre': 'San Fernando'},
            {'com_nombre': 'Chépica'},
            {'com_nombre': 'Chimbarongo'},
            {'com_nombre': 'Lolol'},
            {'com_nombre': 'Nancagua'},
            {'com_nombre': 'Palmilla'},
            {'com_nombre': 'Peralillo'},
            {'com_nombre': 'Placilla'},
            {'com_nombre': 'Pumanque'},
            {'com_nombre': 'Santa Cruz'},
        ]
    }, {
        're_nombre': 'Maule',
        're_numeroregion': 'VII',
        're_numero': 7,
        'comunas': [
            {'com_nombre': 'Talca'},
            {'com_nombre': 'Constitución'},
            {'com_nombre': 'Curepto'},
            {'com_nombre': 'Empedrado'},
            {'com_nombre': 'Maule'},
            {'com_nombre': 'Pelarco'},
            {'com_nombre': 'Pencahue'},
            {'com_nombre': 'Río Claro'},
            {'com_nombre': 'San Clemente'},
            {'com_nombre': 'San Rafael'},
            {'com_nombre': 'Cauquenes'},
            {'com_nombre': 'Chanco'},
            {'com_nombre': 'Pelluhue'},
            {'com_nombre': 'Curicó'},
            {'com_nombre': 'Hualañé'},
            {'com_nombre': 'Licantén'},
            {'com_nombre': 'Molina'},
            {'com_nombre': 'Rauco'},
            {'com_nombre': 'Romeral'},
            {'com_nombre': 'Sagrada Familia'},
            {'com_nombre': 'Teno'},
            {'com_nombre': 'Vichuquén'},
            {'com_nombre': 'Linares'},
            {'com_nombre': 'Colbún'},
            {'com_nombre': 'Longaví'},
            {'com_nombre': 'Parral'},
            {'com_nombre': 'Retiro'},
            {'com_nombre': 'San Javier'},
            {'com_nombre': 'Villa Alegre'},
            {'com_nombre': 'Yerbas Buenas'},
        ]
    }, {
        're_nombre': 'Biobío',
        're_numeroregion': 'VIII',
        're_numero': 8,
        'comunas': [
            {'com_nombre': 'Concepción'},
            {'com_nombre': 'Coronel'},
            {'com_nombre': 'Chiguayante'},
            {'com_nombre': 'Florida'},
            {'com_nombre': 'Hualqui'},
            {'com_nombre': 'Lota'},
            {'com_nombre': 'Penco'},
            {'com_nombre': 'San Pedro de la Paz'},
            {'com_nombre': 'Santa Juana'},
            {'com_nombre': 'Talcahuano'},
            {'com_nombre': 'Tomé'},
            {'com_nombre': 'Hualpén'},
            {'com_nombre': 'Lebu'},
            {'com_nombre': 'Arauco'},
            {'com_nombre': 'Cañete'},
            {'com_nombre': 'Contulmo'},
            {'com_nombre': 'Curanilahue'},
            {'com_nombre': 'Los Álamos'},
            {'com_nombre': 'Tirúa'},
            {'com_nombre': 'Los Ángeles'},
            {'com_nombre': 'Antuco'},
            {'com_nombre': 'Cabrero'},
            {'com_nombre': 'Laja'},
            {'com_nombre': 'Mulchén'},
            {'com_nombre': 'Nacimiento'},
            {'com_nombre': 'Negrete'},
            {'com_nombre': 'Quilaco'},
            {'com_nombre': 'Quilleco'},
            {'com_nombre': 'San Rosendo'},
            {'com_nombre': 'Santa Bárbara'},
            {'com_nombre': 'Tucapel'},
            {'com_nombre': 'Yumbel'},
            {'com_nombre': 'Alto Bío-Bío'},
            {'com_nombre': 'Chillán'},
            {'com_nombre': 'Bulnes'},
            {'com_nombre': 'Cobquecura'},
            {'com_nombre': 'Coelemu'},
            {'com_nombre': 'Coihueco'},
            {'com_nombre': 'Chillán Viejo'},
            {'com_nombre': 'El Carmen'},
            {'com_nombre': 'Ninhue'},
            {'com_nombre': 'Ñiquén'},
            {'com_nombre': 'Pemuco'},
            {'com_nombre': 'Pinto'},
            {'com_nombre': 'Portezuelo'},
            {'com_nombre': 'Quillón'},
            {'com_nombre': 'Quirihue'},
            {'com_nombre': 'Ránquil'},
            {'com_nombre': 'San Carlos'},
            {'com_nombre': 'San Fabián'},
            {'com_nombre': 'San Ignacio'},
            {'com_nombre': 'San Nicolás'},
            {'com_nombre': 'Treguaco'},
            {'com_nombre': 'Yungay'},
        ]
    }, {
        're_nombre': 'La Araucanía',
        're_numeroregion': 'IX',
        're_numero': 9,
        'comunas': [
            {'com_nombre': 'Temuco'},
            {'com_nombre': 'Carahue'},
            {'com_nombre': 'Cunco'},
            {'com_nombre': 'Curarrehue'},
            {'com_nombre': 'Freire'},
            {'com_nombre': 'Galvarino'},
            {'com_nombre': 'Gorbea'},
            {'com_nombre': 'Lautaro'},
            {'com_nombre': 'Loncoche'},
            {'com_nombre': 'Melipeuco'},
            {'com_nombre': 'Nueva Imperial'},
            {'com_nombre': 'Padre las Casas'},
            {'com_nombre': 'Perquenco'},
            {'com_nombre': 'Pitrufquén'},
            {'com_nombre': 'Pucón'},
            {'com_nombre': 'Saavedra'},
            {'com_nombre': 'Teodoro Schmidt'},
            {'com_nombre': 'Toltén'},
            {'com_nombre': 'Vilcún'},
            {'com_nombre': 'Villarrica'},
            {'com_nombre': 'Cholchol'},
            {'com_nombre': 'Angol'},
            {'com_nombre': 'Collipulli'},
            {'com_nombre': 'Curacautín'},
            {'com_nombre': 'Ercilla'},
            {'com_nombre': 'Lonquimay'},
            {'com_nombre': 'Los Sauces'},
            {'com_nombre': 'Lumaco'},
            {'com_nombre': 'Purén'},
            {'com_nombre': 'Renaico'},
            {'com_nombre': 'Traiguén'},
            {'com_nombre': 'Victoria'},
        ]
    }, {
        're_nombre': 'Los Lagos',
        're_numeroregion': 'X',
        're_numero': 10,
        'comunas': [
            {'com_nombre': 'Puerto Montt'},
            {'com_nombre': 'Calbuco'},
            {'com_nombre': 'Cochamó'},
            {'com_nombre': 'Fresia'},
            {'com_nombre': 'Frutillar'},
            {'com_nombre': 'Los Muermos'},
            {'com_nombre': 'Llanquihue'},
            {'com_nombre': 'Maullín'},
            {'com_nombre': 'Puerto Varas'},
            {'com_nombre': 'Castro'},
            {'com_nombre': 'Ancud'},
            {'com_nombre': 'Chonchi'},
            {'com_nombre': 'Curaco de Vélez'},
            {'com_nombre': 'Dalcahue'},
            {'com_nombre': 'Puqueldón'},
            {'com_nombre': 'Queilén'},
            {'com_nombre': 'Quellón'},
            {'com_nombre': 'Quemchi'},
            {'com_nombre': 'Quinchao'},
            {'com_nombre': 'Osorno'},
            {'com_nombre': 'Puerto Octay'},
            {'com_nombre': 'Purranque'},
            {'com_nombre': 'Puyehue'},
            {'com_nombre': 'Río Negro'},
            {'com_nombre': 'San Juan de La Costa'},
            {'com_nombre': 'San Pablo'},
            {'com_nombre': 'Chaitén'},
            {'com_nombre': 'Futaleufú'},
            {'com_nombre': 'Hualaihué'},
            {'com_nombre': 'Palena'},
        ]
    }, {
        're_nombre': 'Aisén del General Carlos Ibáñez del Campo',
        're_numeroregion': 'XI',
        're_numero': 11,
        'comunas': [
            {'com_nombre': 'Coihaique'},
            {'com_nombre': 'Lago Verde'},
            {'com_nombre': 'Aysen'},
            {'com_nombre': 'Cisnes'},
            {'com_nombre': 'Guaitecas'},
            {'com_nombre': 'Cochrane'},
            {'com_nombre': 'O\'Higgins'},
            {'com_nombre': 'Tortel'},
            {'com_nombre': 'Chile Chico'},
            {'com_nombre': 'Río Ibáñez'},
        ]
    }, {
        're_nombre': 'Magallanes y de la Antártica Chilena',
        're_numeroregion': 'XII',
        're_numero': 12,
        'comunas': [
            {'com_nombre': 'Punta Arenas'},
            {'com_nombre': 'Laguna Blanca'},
            {'com_nombre': 'Río Verde'},
            {'com_nombre': 'San Gregorio'},
            {'com_nombre': 'Cabo de Hornos'},
            {'com_nombre': 'Antártica'},
            {'com_nombre': 'Porvenir'},
            {'com_nombre': 'Primavera'},
            {'com_nombre': 'Timaukel'},
            {'com_nombre': 'Natales'},
            {'com_nombre': 'Torres del Paine'},
        ]
    }, {
        're_nombre': 'Los Ríos',
        're_numeroregion': 'XIV',
        're_numero': 14,
        'comunas': [
            {'com_nombre': 'Valdivia'},
            {'com_nombre': 'Corral'},
            {'com_nombre': 'Lanco'},
            {'com_nombre': 'Los Lagos'},
            {'com_nombre': 'Máfil'},
            {'com_nombre': 'Mariquina'},
            {'com_nombre': 'Paillaco'},
            {'com_nombre': 'Panguipulli'},
            {'com_nombre': 'La Unión'},
            {'com_nombre': 'Futrono'},
            {'com_nombre': 'Lago Ranco'},
            {'com_nombre': 'Río Bueno'},
        ]
    }, {
        're_nombre': 'Arica y Parinacota',
        're_numeroregion': 'XV',
        're_numero': 15,
        'comunas': [
            {'com_nombre': 'Arica'},
            {'com_nombre': 'Camarones'},
            {'com_nombre': 'Putre'},
            {'com_nombre': 'General Lagos'},
        ]
    }]
    #
    lst_log.append({'text': '* Agregando:'})
    for r in lst_regiones:
        re = Region.objects.using(ba_nombre).filter(re_numero=r['re_numero'])
        if not re.exists():
            re = Region()
            re.re_nombre = r['re_nombre']
            re.pais = pais
            re.re_numeroregion = r['re_numeroregion']
            re.re_numero = r['re_numero']
            re.save(using=ba_nombre)
            lst_log.append({'text': '** Región : %s' % r['re_nombre'].title()})
            for c in r['comunas']:
                co = Comuna()
                co.com_nombre = c['com_nombre']
                co.region = re
                co.save(using=ba_nombre)
                lst_log.append({'text': '****** Comuna : %s' % c['com_nombre'].title()})

            lst_log.append({'text': '-----------------------------'})
        else:
            lst_log.append({'text': 'La región %s y sus comunas ya existen' % r['re_nombre']})

    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '* Agregando CCFC:'})
    lst_cajas_compensasiones = [{
        'cc_nombre': ' Asociación Gremial de Cajas de Compensación ',
        'cc_codigo': '01',
    }, {
        'cc_nombre': 'Caja 18 de Septiembre ',
        'cc_codigo': '02',
    }, {
        'cc_nombre': 'Caja Gabriela Mistral',
        'cc_codigo': '03',
    }, {
        'cc_nombre': 'Caja los Andes',
        'cc_codigo': '04',
    }, {
        'cc_nombre': 'Caja Los Heroes',
        'cc_codigo': '05',
    }, {
        'cc_nombre': 'La Araucana',
        'cc_codigo': '06',
    }, {
        'cc_nombre': 'Pensionados',
        'cc_codigo': '07',
    }]

    for c in lst_cajas_compensasiones:
        cc = CajasCompensacion.objects.using(ba_nombre).filter(cc_codigo=c['cc_codigo'])
        if not cc.exists():
            cc = CajasCompensacion()
            cc.cc_nombre = c['cc_nombre']
            cc.cc_codigo = c['cc_codigo']
            cc.save(using=ba_nombre)
            lst_log.append({'text': '** CCFC : %s' % c['cc_nombre'].title()})
            lst_log.append({'text': '-- CCFC cargados con éxito...'})
        else:
            lst_log.append({'text': 'La entidad %s ya existe' % c['cc_nombre'].title()})

        lst_log.append({'text': '-----------------------------'})

    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- *************************************** --'})

    lstSalud = [
        {'sa_nombre': 'Fonasa', 'sa_codigo': '100', 'sa_tipo': 'F'},
        {'sa_nombre': 'Banmédica S.A.', 'sa_codigo': '99', 'sa_tipo': 'I'},
        {'sa_nombre': 'Chuquicamata Ltda.', 'sa_codigo': '65', 'sa_tipo': 'I'},
        {'sa_nombre': 'Colmena Golden Cross S.A.', 'sa_codigo': '67', 'sa_tipo': 'I'},
        {'sa_nombre': 'Consalud S.A.', 'sa_codigo': '107', 'sa_tipo': 'I'},
        {'sa_nombre': 'Cruz Blanca S.A.', 'sa_codigo': '78', 'sa_tipo': 'I'},
        {'sa_nombre': 'Cruz del Norte Ltda.', 'sa_codigo': '94', 'sa_tipo': 'I'},
        {'sa_nombre': 'Nueva Masvida S.A.', 'sa_codigo': '81', 'sa_tipo': 'I'},
        {'sa_nombre': 'Fundación Ltda.', 'sa_codigo': '76', 'sa_tipo': 'I'},
        {'sa_nombre': 'Fusat Ltda.', 'sa_codigo': '63', 'sa_tipo': 'I'},
        {'sa_nombre': 'Río Blanco Ltda.', 'sa_codigo': '68', 'sa_tipo': 'I'},
        {'sa_nombre': 'San Lorenzo Ltda.', 'sa_codigo': '62', 'sa_tipo': 'I'},
        {'sa_nombre': 'Vida Tres S.A.', 'sa_codigo': '80', 'sa_tipo': 'I'},
    ]

    lst_log.append({'text': '-- Listando entidades de salud...'})
    for salud in lstSalud:
        cc = Salud.objects.using(ba_nombre).filter(sa_codigo=salud['sa_codigo'])
        if not cc.exists():
            s = Salud()
            s.sa_nombre = salud['sa_nombre']
            s.sa_codigo = salud['sa_codigo']
            s.sa_tipo = salud['sa_tipo']
            s.save(using=ba_nombre)

            lst_log.append({'text': '-- La entidad %s fue creada con éxito...' % salud['sa_nombre']})
        else:
            lst_log.append({'text': '-- La entidad %s ya existe...' % salud['sa_nombre']})

    lst_log.append({'text': '-- Entidades de salud creadas exitosamente...'})
    lst_log.append({'text': '-- *************************************** --'})

    lstPrevision = [
        {'afp_codigoprevired': '33', 'afp_nombre': 'Capital', 'afp_tasatrabajadordependiente': 11.44, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.97},
        {'afp_codigoprevired': '03', 'afp_nombre': 'Cuprum', 'afp_tasatrabajadordependiente': 11.44, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.97},
        {'afp_codigoprevired': '05', 'afp_nombre': 'Habitat', 'afp_tasatrabajadordependiente': 11.27, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.80},
        {'afp_codigoprevired': '29', 'afp_nombre': 'PlanVital', 'afp_tasatrabajadordependiente': 11.16, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.69},
        {'afp_codigoprevired': '08', 'afp_nombre': 'ProVida', 'afp_tasatrabajadordependiente': 11.45, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.98},
        {'afp_codigoprevired': '34', 'afp_nombre': 'Modelo', 'afp_tasatrabajadordependiente': 10.77, 'afp_sis': 1.53,
         'afp_tasatrabajadorindependiente': 12.30},
    ]

    for prev in lstPrevision:
        a = Afp.objects.using(ba_nombre).filter(afp_codigoprevired=prev['afp_codigoprevired'])
        if not a.exists():
            a = Afp()
            a.afp_codigoprevired = prev['afp_codigoprevired']
            a.afp_nombre = prev['afp_nombre']
            a.afp_tasatrabajadordependiente = prev['afp_tasatrabajadordependiente']
            a.afp_sis = prev['afp_sis']
            a.afp_tasatrabajadorindependiente = prev['afp_tasatrabajadorindependiente']
            a.save(using=ba_nombre)
            lst_log.append({'text': '-- La entidad %s fue creada con éxito...' % prev['afp_nombre']})
        else:
            lst_log.append({'text': '-- La entidad %s ya existe...' % prev['afp_nombre']})

    lst_log.append({'text': '-- Entidades de previsionales fueron creadas exitosamente...'})
    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- Listando Bancos...'})
    lst_log.append({'text': '-- Agregando:'})

    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- *************************************** --'})
    lst_log.append({'text': '-- Agregando parámetros...'})


    la_base.ba_adddprc = 'S'
    la_base.save()

    return lst_log


# -------------------------------------
@login_required
@csrf_exempt
def ajaxLlenadoTablaGeneral(request, baseId, is_ajax):
    la_base = BaseEmpresa.objects.get(ba_id=baseId)
    ba_nombre = la_base.ba_conexion

    lst_log = []
    lst_valores = [
        {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '1',
            'tg_cod_ext': None,
            'tg_descripcion': '30 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '2',
            'tg_cod_ext': None,
            'tg_descripcion': '60 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '3',
            'tg_cod_ext': None,
            'tg_descripcion': '90 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '4',
            'tg_cod_ext': None,
            'tg_descripcion': 'Al contado',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '5',
            'tg_cod_ext': None,
            'tg_descripcion': 'Pago con cheque al día',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '6',
            'tg_cod_ext': None,
            'tg_descripcion': 'Pago con cheque 30 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '7',
            'tg_cod_ext': None,
            'tg_descripcion': 'Pago con cheque 60 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_proveedor',
            'tg_codigo': '8',
            'tg_cod_ext': None,
            'tg_descripcion': 'Pago con cheque 90 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        },
        # ------------------------------
        {
            'tg_nomtabla': 'vencimiento_tipo_cliente',
            'tg_codigo': '1',
            'tg_cod_ext': None,
            'tg_descripcion': '30 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_cliente',
            'tg_codigo': '2',
            'tg_cod_ext': None,
            'tg_descripcion': '60 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_cliente',
            'tg_codigo': '3',
            'tg_cod_ext': None,
            'tg_descripcion': '90 días',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }, {
            'tg_nomtabla': 'vencimiento_tipo_cliente',
            'tg_codigo': '4',
            'tg_cod_ext': None,
            'tg_descripcion': 'Al contado',
            'tg_num_aux': None,
            'tg_fecha_aux': None,
            'tg_text_aux': None,
            'tg_valor': None,
        }
    ]

    for x in lst_valores:
        i = TablaGeneral.objects.using(ba_nombre).filter(tg_nomtabla=x['tg_nomtabla'], tg_codigo=x['tg_codigo'])

        if not i.exists():
            i = TablaGeneral()
            i.tg_nomtabla = x['tg_nomtabla']
            i.tg_codigo = x['tg_codigo']
            i.tg_cod_ext = x['tg_cod_ext']
            i.tg_descripcion = x['tg_descripcion']
            i.tg_num_aux = x['tg_num_aux']
            i.tg_fecha_aux = x['tg_fecha_aux']
            i.tg_text_aux = x['tg_text_aux']
            i.tg_valor = x['tg_valor']
            i.save(using=ba_nombre)
            print("El dato '{}' fue agregado con éxito a la tabla '{}'".format(x['tg_descripcion'], x['tg_nomtabla']))
            lst_log.append({'text': 'El dato "{}" fue agregado con éxito a la tabla "{}"'.format(x['tg_descripcion'],
                                                                                                 x['tg_nomtabla'])})
        else:
            print("El dato '{}' ya existe en la tabla '{}'".format(x['tg_descripcion'], x['tg_nomtabla']))
            lst_log.append(
                {'text': 'El dato "{}" ya existe en la tabla "{}"'.format(x['tg_descripcion'], x['tg_nomtabla'])})

    if is_ajax:
        html = {
            'lst_log': lst_log,
        }
        response = json.dumps(html)
        return HttpResponse(response, content_type='application/json')
    else:
        return lst_log
