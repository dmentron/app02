# -*- encoding: utf-8 -*-
import datetime
# Create your views here.
import json
import os
import argparse
import urllib.request
import wget

from bs4 import BeautifulSoup

import django
import django.conf as conf
import psycopg2
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT 
from datetime import datetime, timedelta
from django.contrib.auth import login, authenticate
from pyxb.bundles.wssplat.raw.soap12 import faultcodeEnum

from bases.forms import BaseEmpresaForm, UserFormBases, LoginForm
from bases.models import BaseEmpresa, ClienteActivo
from gaia.settings import PORT_LOCALHOST, NAME_HOST, STATICFILES_DIRS
from gaia.utils import elige_choices, creacionUsuarioSesion
from seguridad.models import Usuario


def bases_login(request):
    """
    :param request:
    :return: pagina de logeo
    """

    data = {
        'form': LoginForm,
    }
    return render(request, 'bases/bases_login.html', data)


def dashboard(request):
    """
    :param request:
    :return: pagina de logeo
    """

    data = {

    }
    return render(request, 'bases/dashboard.html', data)


def web_scraping(request):
    """
    :param request:
    :return: pagina de logeo %2F
    """

    lst_css = []
    lst_a = []
    lst_img = []
    lst_js = []

    data = {
        'lst_css': lst_css,
        'lst_a': lst_a,
        'lst_img': lst_img,
        'lst_js': lst_js,
    }
    return render(request, 'bases/webscraping.html', data)


def armar_instruccion(request):
    list_ch = 'BORRADOR'
    list_pull = ['FIX', 'FEATURE', 'RELEASE', 'ERROR']
    dic_meses = {
        'ENE': 'ENE',
        'FEB': 'FEB',
        'MAR': 'MAR',
        'ABR': 'ABR',
        'MAY': 'MAY',
        'JUN': 'JUN',
        'JUL': 'JUL',
        'AGO': 'AGO',
        'SEP': 'SEP',
        'OCT': 'OCT',
        'NOV': 'NOV',
        'DIC': 'DIC',
    }

    dic_mod = {
        'ABA': 'Abastecimiento',
        'VTA': 'Venta',
        'EXIS': 'Existencia',
        'FIN': 'Finanzas',
        'TESO': 'Tesoreria',
        'PROC': 'Procesos',
        'MANTEN': 'Mantenedores',
        'CONFIG': 'Configuracion',
        'TODOS': 'Todos',
    }

    hoy = datetime.now()
    anio_actual = hoy.year
    mes_actual = hoy.month

    data = {
        'anio_actual': anio_actual,
        'mes_actual': mes_actual,
        'list_ch': list_ch,
        'list_pull': list_pull,
        'dic_meses': dic_meses,
        'dic_mod': dic_mod,
    }

    return render(request, 'bases/armar_instruccion.html', data)


@login_required
def listado_bases(request):
    lst_bases = []
    contador = 0
    bEmpresas = BaseEmpresa.objects.all()
    for e in bEmpresas:
        contador += 1
        lst_bases.append({
            'num': contador,
            'ba_nameemp': e.ba_nameemp,
            'ba_name': e.ba_name,
            'ba_esquema': e.ba_esquema,
            'ba_host': e.ba_host,
            'ba_port': e.ba_port,
            'ba_activa': elige_choices(BaseEmpresa.OPCIONES, e.ba_activa),
            'ba_id': e.ba_id,
            'activa': e.ba_activa,
            'ba_link': e.ba_link,
            'ba_creada': e.ba_creada,
        })

    data = {
        'lst_bases': lst_bases,
    }
    return render(request, 'bases/listado_bases.html', data)


def add_base_de_datos(request):
    """
    :param request:
    :return: pagina de logeo
    """
    lst_bases = []
    lista_err = []

    if request.POST:
        formBaseEmpresaForm = BaseEmpresaForm(request.POST)
        if formBaseEmpresaForm.is_valid():
            form = formBaseEmpresaForm.save(commit=False)
            form.ba_esquema = request.POST['ba_esquema']
            form.ba_activa = 'N'

            format_str = '%Y-%m-%d'
            a = datetime.strptime(request.POST['ba_fechaingreso'], format_str)
            b = datetime.strptime(request.POST['ba_fechatermino'], format_str)

            form.ba_fechaingreso = a
            form.ba_fechatermino = b
            
            ba_esquema = request.POST['ba_esquema']
            linkEmpresa = f'http://{ba_esquema}.{NAME_HOST}{PORT_LOCALHOST}/login'

            form.ba_link = linkEmpresa

            form.save()

            return redirect('editar_base', form.ba_id)
        else:
            error = True
            for field in formBaseEmpresaForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
    else:
        formBaseEmpresaForm = BaseEmpresaForm()

        formBaseEmpresaForm.fields['ba_host'].widget.attrs['readonly'] = True
        formBaseEmpresaForm.fields['ba_host'].initial = 'localhost'

        formBaseEmpresaForm.fields['ba_esquema'].widget.attrs['readonly'] = True
        formBaseEmpresaForm.fields['ba_name'].widget.attrs['readonly'] = True
        formBaseEmpresaForm.fields['ba_conexion'].widget.attrs['readonly'] = True

    data = {
        'formBaseEmpresaForm': formBaseEmpresaForm,
        'isEdit': False,
    }

    return render(request, 'bases/add_edit_bases.html', data)


def editar_base(request, id_base):
    lista_err = []
    lista_usuarios_admin = []
    baseCreada = False
    bEmpresa = BaseEmpresa.objects.get(ba_id=id_base)
    formBaseEmpresaForm = BaseEmpresaForm(request.POST or None, instance=bEmpresa)

    try:
        # se crea la conexion
        conexion = psycopg2.connect(dbname=bEmpresa.ba_name, user=bEmpresa.ba_user, host=bEmpresa.ba_host,
                                    password=bEmpresa.ba_password)
        conexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE
        request.session['error_bases'] = False
    except:
        error_bases = {
            'mensaje': 'No existe la base de datos, primero debe crear la base, favor de hacer click en el botón '
                       '"Crear base"',
            'error': True
        }
        request.session['error_bases'] = error_bases
        redirect('editar_base', id_base)

    if bEmpresa.ba_creada == 'S':
        baseCreada = True

    if request.POST:
        if formBaseEmpresaForm.is_valid():
            form = formBaseEmpresaForm.save(commit=False)
            form.ba_esquema = request.POST['ba_esquema']
            form.ba_activa = 'N'
            form.save()
            # aqui redirecciona al momento de crear un documento, se redirecciona a la funcion de edita
            try:
                ca = ClienteActivo.objects.using(form.ba_conexion).get(cac_id=form.ba_idclienteactivo)
            except:
                ca = ClienteActivo()

            ca.cac_cantempleados = form.ba_cantidadusuarios
            ca.save(using=form.ba_conexion)
        else:
            error = True
            for field in formBaseEmpresaForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    formBaseEmpresaForm.fields['ba_host'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_nameemp'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_name'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_conexion'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_fechaingreso'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_esquema'].widget.attrs["readonly"] = True
    formBaseEmpresaForm.fields['ba_esquema'].initial = bEmpresa.ba_esquema

    lstUsuarios = []
    if bEmpresa.ba_creada == 'S':
        try:
            usuarios = Usuario.objects.using(bEmpresa.ba_conexion).filter(user__is_staff=True)
            contador = 0
            for x in usuarios:
                contador += 1
                usr = User.objects.using(bEmpresa.ba_conexion).get(id=x.user_id)

                lstUsuarios.append({
                    'contador': contador,
                    'id': x.user_id,
                    'first_name': usr.first_name,
                    'last_name': usr.last_name,
                    'usu_nombreusuario': x.usu_nombreusuario,
                    'usu_passwordusuario': x.usu_passwordusuario,
                    'is_staff': usr.is_staff,
                })
        except:
            pass
    else:
        lstUsuarios = []

    data = {
        'formBaseEmpresaForm': formBaseEmpresaForm,
        'frm': UserFormBases(),
        'isEdit': True,
        'usuarios': lstUsuarios,
        'idbase': id_base,
        'nombre_base': bEmpresa.ba_name.upper(),
        'fecha_ini': bEmpresa.ba_fechaingreso,
        'fecha_fin': bEmpresa.ba_fechatermino,
        'baseCreada': baseCreada,
        'editar': True,
    }
    return render(request, 'bases/add_edit_bases.html', data)


@login_required
@csrf_exempt
def create_database(request):
    lst_log = []
    lista_err = []
    existe_base = False

    la_base = BaseEmpresa.objects.get(ba_id=request.POST['ba_id'])

    ba_nombre = la_base.ba_name
    ba_usuario = la_base.ba_user
    ba_host = la_base.ba_host
    ba_password = la_base.ba_password

    try:
        # se crea la conexion
        conexion = psycopg2.connect(dbname='postgres', user=ba_usuario, host=ba_host, password=ba_password)
        conexion.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE
    except Exception as ex:
        lista_err.append({
            'label': 'DATABASE',
            'error': str(ex),
        })
        return JsonResponse({'lista_err': lista_err})

    # se abre cursos
    cur = conexion.cursor()
    # se crea la base
    try:
        # se crea la base
        cur.execute("CREATE DATABASE %s ;" % ba_nombre)
        lst_log.append({'text': '-- CREATE DATABASE %s ...exito!' % ba_nombre})
    except:
        lista_err.append({
            'label': 'DATABASE',
            'error': "La base de datos ya existe",
        })
        return JsonResponse({'lista_err': lista_err})

    log_migrate = crearMigrate(request, la_base.ba_id, False)

    html = {
        'lst_log': lst_log,
        'log_migrate': log_migrate,
        'lista_err': lista_err,
        'base_creada': la_base.ba_creada,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


# -------------------------------------
@login_required
@csrf_exempt
def armar_estructura_carpeta_empresa(request):
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

    la_base = BaseEmpresa.objects.get(ba_id=int(request.POST['base_id']))
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
    #
    # directorio_template = STATICFILES_DIRS[1] + "/" + ba_conexion
    # try:
    #     os.stat(directorio_template)
    # except:
    #     os.mkdir(directorio_template)
    #
    # cActivo = ClienteActivo.objects.using(la_base.ba_name).get(cac_id=la_base.ba_idclienteactivo)
    # cActivo.cac_rutadocumentos = directorio_documentos
    # cActivo.cac_rutadstatic = directorio_static
    # cActivo.cac_rutausuarios = directorio_usuarios
    # cActivo.save(using=ba_conexion)

    lst_log.append({'text': 'Directorios guardado con éxito...'})

    html = {
        'lst_log': lst_log,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
@csrf_exempt
def datos_base(request):
    ba_id = request.POST['ba_id']

    b = BaseEmpresa.objects.get(ba_id=ba_id)

    conexion = {
        'CONNECT': b.ba_conexion,
        'ENGINE': elige_choices(BaseEmpresa.ENGINE, b.ba_engine),
        'NAME': b.ba_name,
        'USER': b.ba_user,
        'PASSWORD': b.ba_password,
        'HOST': b.ba_host,
        'PORT': b.ba_port,
    }

    html = {
        'conexion': conexion,
        'connect': b.ba_conexion,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
@csrf_exempt
def crearMigrate(request, baseId, is_ajax):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gaia.settings")
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

    call_command('migrate', database=la_base.ba_conexion)

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

# @csrf_exempt
# @login_required
# def add_usuario_admin(request, emp_id):
#     lista_err = []
#     la_empresa = BaseEmpresa.objects.get(ba_id=emp_id)
#     is_error = False
#
#     frm = UserFormBases(request.POST or None)
#
#     if request.POST:
#         with transaction.atomic():
#             if frm.is_valid():
#                 try:
#                     # form = frm.save(commit=False)
#                     form = User()
#
#                     form.username = request.POST['username']
#                     form.first_name = request.POST['first_name']
#                     form.last_name = request.POST['last_name']
#                     form.email = request.POST['email']
#                     form.set_password(request.POST['password1'])
#                     form.is_staff = True
#                     form.is_superuser = True
#                     form.save(using=la_empresa.ba_conexion)
#                     # ****************************
#                     u = Usuario()
#                     u.user = form
#
#                     date_str = '31/12/2999'
#                     format_str = '%d/%m/%Y'
#                     datetime_obj = datetime.datetime.strptime(date_str, format_str)
#
#                     u.usu_rut = form.username
#                     u.usu_tipousuario = 1
#                     u.usu_fechanacimiento = datetime_obj
#                     u.usu_nombreusuario = form.username
#                     u.usu_passwordusuario = request.POST['password1']
#                     u.save(using=la_empresa.ba_conexion)
#                     # ****************************
#
#                     return redirect('bases:editarBaseDeDato', emp_id)
#
#                 except Exception as inst:
#                     print(type(inst))  # la instancia de excepción
#                     print(inst.args)  # argumentos guardados en .args
#                     print(inst)  # __str__ permite imprimir args directamente,
#
#                     lista_err.append("ERROR" + ': ' + str(inst))
#                     is_error = True
#             else:
#                 for field in frm:
#                     el_error = ""
#                     for error in field.errors:
#
#                         print(error)
#
#                         if error == 'Enter a valid email address.':
#                             el_error = "- Ingrese una dirección de correo valida."
#
#                         if error == "This password is too short. It must contain at least 8 characters.":
#                             el_error = '- La contraseña debe tener un minimo de 8 caracteres'
#
#                         if error == "The two password fields didn't match.":
#                             el_error = '- Al repetir la contraseña debe ser igual a la ingresada del campo contraseña'
#
#                         if error == "This password is too common.":
#                             el_error = '- Esta contraseña es demasiado común'
#
#                         lista_err.append(el_error)
#
#                 for er in lista_err:
#                     print("Error: ", er)
#
#                 is_error = True
#     html = {
#         'nombre_empresa': la_empresa.ba_nameemp,
#         'error': is_error,
#         'lista_err': lista_err
#     }
#     response = json.dumps(html)
#     return HttpResponse(response, content_type='application/json')
#
#
# @csrf_exempt
# @login_required
# def editUsuarioAdmin(request, emp_id, usu_id):
#     lista_err = []
#     la_empresa = BaseEmpresa.objects.get(ba_id=emp_id)
#     is_error = False
#
#     frm = UserFormBases(request.POST or None)
#
#     if request.POST:
#         with transaction.atomic():
#             if frm.is_valid():
#                 try:
#                     # form = frm.save(commit=False)
#                     form = User.objects.using(la_empresa.ba_conexion).get(id=usu_id)
#
#                     form.username = request.POST['username']
#                     form.first_name = request.POST['first_name']
#                     form.last_name = request.POST['last_name']
#                     form.email = request.POST['email']
#                     form.set_password(request.POST['password1'])
#                     form.save(using=la_empresa.ba_conexion)
#
#                     # ****************************
#                     u = Usuario.objects.using(la_empresa.ba_conexion).get(user_id=form.id)
#                     u.usu_rut = form.username
#                     u.usu_nombreusuario = form.username
#                     u.usu_passwordusuario = request.POST['password1']
#                     u.save(using=la_empresa.ba_conexion)
#                     # ****************************
#
#                     return redirect('bases:editarBaseDeDato', emp_id)
#
#                 except Exception as inst:
#                     print(type(inst))  # la instancia de excepción
#                     print(inst.args)  # argumentos guardados en .args
#                     print(inst)  # __str__ permite imprimir args directamente,
#
#                     lista_err.append("ERROR" + ': ' + str(inst))
#                     is_error = True
#             else:
#                 for field in frm:
#                     el_error = ""
#                     for error in field.errors:
#                         if error == 'Enter a valid email address.':
#                             el_error = "- Ingrese una dirección de correo valida."
#
#                         if error == "This password is too short. It must contain at least 8 characters.":
#                             el_error = '- La contraseña debe tener un minimo de 8 caracteres'
#
#                         if error == "The two password fields didn't match.":
#                             el_error = '- Al repetir la contraseña debe ser igual a la ingresada del campo contraseña'
#
#                         lista_err.append(el_error)
#
#                 for er in lista_err:
#                     print("Error: ", er)
#
#                 is_error = True
#     html = {
#         'nombre_empresa': la_empresa.ba_nameemp,
#         'error': is_error,
#         'lista_err': lista_err
#     }
#     response = json.dumps(html)
#     return HttpResponse(response, content_type='application/json')
#
#
# @login_required
# @csrf_exempt
# def obtenerDatosUsuario(request, user_id, bd_id):
#     la_empresa = BaseEmpresa.objects.get(ba_id=bd_id)
#     el_usuario = Usuario.objects.using(la_empresa.ba_conexion).get(user__id=user_id)
#     el_user = User.objects.using(la_empresa.ba_conexion).get(id=user_id)
#
#     html = {
#
#         'username': el_user.username,
#         'first_name': el_user.first_name,
#         'last_name': el_user.last_name,
#         'is_staff': el_user.is_staff,
#         'mail': el_user.email,
#         'usu_nombreusuario': el_usuario.usu_nombreusuario,
#         'usu_passwordusuario': el_usuario.usu_passwordusuario,
#
#     }
#     response = json.dumps(html)
#     return HttpResponse(response, content_type='application/json')
#
#
# @login_required
# def activarBase(request, baseId, accion):
#     la_empresa = BaseEmpresa.objects.get(ba_id=baseId)
#     la_empresa.ba_activa = accion
#     la_empresa.save()
#
#     directorio_static = STATICFILES_DIRS[0] + "\\" + la_empresa.ba_conexion
#     directorio_documentos = directorio_static + "\\documentos"
#     directorio_usuarios = directorio_static + "\\usuarios"
#
#     cActivo = ClienteActivo.objects.using(la_empresa.ba_name).get(cac_id=la_empresa.ba_idclienteactivo)
#     cActivo.cac_activo = 'S'
#     cActivo.cac_rutabase = BASE_COMMAND
#     cActivo.cac_rutadocumentos = directorio_documentos
#     cActivo.cac_rutadstatic = STATICFILES_DIRS[0] + "\\" + la_empresa.ba_conexion
#     cActivo.cac_rutausuarios = directorio_usuarios
#     cActivo.cac_nombrebase = la_empresa.ba_conexion
#     cActivo.cac_nombreimagenlogo = ''
#     cActivo.save(using=la_empresa.ba_name)
#
#     return redirect('bases:listado_bases')
#
#
# @login_required
# def borrarUsuario(request, baseId, usuario):
#     la_empresa = BaseEmpresa.objects.get(ba_id=baseId)
#     usuarios = User.objects.using(la_empresa.ba_name).get(id=usuario)
#     usuarios.delete(using=la_empresa.ba_name)
#     return redirect('bases:editarBaseDeDato', baseId)
#
#
# @login_required
# def documentoPorDefecto(request):
#     lstTipoDocumentos = []
#     contador = 0
#
#     docs = TipoDocumentos.objects.all()
#
#     for x in docs:
#         contador += 1
#         lstTipoDocumentos.append({
#             'contador': contador,
#             'tdl_id': x.tdl_id,
#             'tdl_codigo': x.tdl_codigo,
#             'tdl_descripcion': x.tdl_descripcion,
#             'tdl_activo': elige_choices(TipoDocumentos.OPCIONES, x.tdl_activo),
#             'tdl_pordefecto': elige_choices(TipoDocumentos.OPCIONES, x.tdl_pordefecto),
#             'tdl_filtrodoc': elige_choices(TipoDocumentos.FILTRO_DOCS, x.tdl_filtrodoc),
#         })
#
#     data = {
#         'lstTipoDocumentos': lstTipoDocumentos,
#     }
#     return render(request, 'bases/documentos_por_defecto.html', data)
#
#
# @login_required
# def addNuevoTipoDocumento(request):
#     lista_err = []
#     xerror = False
#     frmTipoDocumentosForm = TipoDocumentosForm(request.POST or None)
#     fecha_codigo = datetime.datetime.strftime(datetime.datetime.now(), "%d%m%Y_%H%M%f")
#     if request.POST:
#         if frmTipoDocumentosForm.is_valid():
#             form = frmTipoDocumentosForm.save(commit=False)
#             form.tdl_codigo = fecha_codigo
#             form.tdl_activo = 'S'
#             form.tdl_pordefecto = 'S'
#             form.tdl_filtrodoc = 'DEF'
#             form.save()
#
#             las_bases = BaseEmpresa.objects.filter(ba_creada='S')
#             if las_bases.count() > 0:
#                 for x in las_bases:
#                     t = TipoDocumentos()
#                     t.tdl_codigo = fecha_codigo
#                     t.tdl_descripcion = form.tdl_descripcion
#                     t.tdl_activo = 'S'
#                     t.tdl_pordefecto = 'S'
#                     t.tdl_filtrodoc = 'DEF'
#                     t.save(using=x.ba_conexion)
#
#             return redirect('bases:editNuevoTipoDocumento', form.tdl_id)
#         else:
#             for field in frmTipoDocumentosForm:
#                 for error in field.errors:
#                     lista_err.append(field.label + ': ' + error)
#             for er in lista_err:
#                 print(er)
#             xerror = True
#
#     data = {
#         'frmTipoDocumentosForm': frmTipoDocumentosForm,
#         'error': xerror,
#         'lista_err': lista_err,
#     }
#     return render(request, 'bases/add_nuevo_tipo_documento.html', data)
#
#
# @login_required
# def editNuevoTipoDocumento(request, tdl_id):
#     lista_err = []
#     lst_documentos = []
#     xerror = False
#
#     td = TipoDocumentos.objects.get(tdl_id=tdl_id)
#
#     frmTipoDocumentosForm = TipoDocumentosForm(request.POST or None, instance=td)
#
#     if request.POST:
#
#         if frmTipoDocumentosForm.is_valid():
#             form = frmTipoDocumentosForm.save(commit=False)
#             form.save()
#
#             las_bases = BaseEmpresa.objects.filter(ba_creada='S')
#
#             if las_bases.count() > 0:
#
#                 for x in las_bases:
#                     t = TipoDocumentos.objects.get(tdl_id=tdl_id)
#                     t.tdl_codigo = form.tdl_codigo
#                     t.tdl_descripcion = form.tdl_descripcion
#                     t.tdl_activo = 'S'
#                     t.save(using=x.ba_conexion)
#
#         else:
#             for field in frmTipoDocumentosForm:
#                 for error in field.errors:
#                     lista_err.append(field.label + ': ' + error)
#             for er in lista_err:
#                 print(er)
#             xerror = True
#
#     xDocumentos = Documento.objects.filter(tipoDocumentos=td)
#
#     contador = 0
#     for d in xDocumentos:
#         contador += 1
#         lst_documentos.append({
#             'contador': contador,
#             'doc_nombre': d.doc_nombre,
#             'doc_activo': elige_choices(Documento.OPCIONES, d.doc_activo),
#             'doc_id': d.doc_id,
#         })
#
#     data = {
#         'frmTipoDocumentosForm': frmTipoDocumentosForm,
#         'error': xerror,
#         'lista_err': lista_err,
#         'is_edit': True,
#         'lst_documentos': lst_documentos,
#         'tdl_id': tdl_id,
#     }
#     return render(request, 'bases/add_nuevo_tipo_documento.html', data)
#
#
# @login_required
# def borrarTipoDocumento(request, tdl_id):
#     la_empresa = BaseEmpresa.objects.all()
#     tDocumentos = TipoDocumentos.objects.get(tdl_id=tdl_id)
#     for x in la_empresa:
#         td = TipoDocumentos.objects.using(x.ba_conexion).get(tdl_codigo=tDocumentos.tdl_codigo)
#         td.delete(using=x.ba_conexion)
#     tDocumentos.delete()
#     return redirect('bases:documentoPorDefecto')
#
#
# @login_required
# def agregarDocumentoStandart(request, tdl_id):
#     lista_err = []
#     xerror = False
#
#     frmDocumentoForm = DocumentoGeneralForm(request.POST or None)
#     td = TipoDocumentos.objects.get(tdl_id=tdl_id)
#     if request.POST:
#
#         if frmDocumentoForm.is_valid():
#             form = frmDocumentoForm.save(commit=False)
#             form.tipoDocumentos = td
#
#             name_template = "%s.html" % request.POST['doc_nombre']
#
#             form.doc_template = name_template.replace(' ', '_')
#             form.doc_defecto = 'S'
#             form.doc_fechacreacion = datetime.datetime.now()
#             form.save()
#
#             las_bases = BaseEmpresa.objects.all()
#
#             if las_bases.count() > 0:
#
#                 for x in las_bases:
#                     xtd = TipoDocumentos.objects.using(x.ba_conexion).filter(tdl_codigo=td.tdl_codigo).first()
#
#                     d = Documento()
#                     d.tipoDocumentos = xtd
#                     d.doc_activo = 'S'
#                     d.doc_defecto = form.doc_defecto
#                     d.doc_nombre = form.doc_nombre
#                     d.doc_texto = form.doc_texto
#                     d.doc_template = form.doc_template
#                     d.doc_fechacreacion = form.doc_fechacreacion
#                     d.save(using=x.ba_conexion)
#
#                 html_logo = '{}\n'.format("{% include 'docpdf/style.html' %}")
#                 html_logo += '<table width="100%" border="0" cellspacing="0" cellpadding="0">\n'
#                 html_logo += '<tr>\n'
#                 html_logo += '<td><img class="img-responsive" width="151" height="48" src="{{logo}}"></td>\n'
#                 html_logo += '<td></td>\n'
#                 html_logo += '</tr>\n'
#                 html_logo += '<tr>\n'
#                 html_logo += '<td colspan="2">\n<br/>\n<br/>\n<br/>{}</td>\n'.format(form.doc_texto)
#                 html_logo += '</tr>\n'
#                 html_logo += '</table>'
#
#                 # ruta_doc = "{}\\docpdf\\doc_generales\\{}".format(STATICFILES_DIRS[1], form.doc_template)
#                 ruta_doc = "{}/docpdf/{}".format(STATICFILES_DIRS[1], form.doc_template)
#                 print(ruta_doc)
#
#                 file = open(ruta_doc, "w")
#                 file.write(html_logo)
#                 file.close()
#             return redirect('bases:editarDocumentoStandart', tdl_id, form.doc_id)
#         else:
#             for field in frmDocumentoForm:
#                 for error in field.errors:
#                     lista_err.append(field.label + ': ' + error)
#             for er in lista_err:
#                 print(er)
#             xerror = True
#
#     lstVariables = listadoVariableUsuarioEmpesa()
#
#     data = {
#         'error': xerror,
#         'lista_err': lista_err,
#         'tdl_id': tdl_id,
#         'frmDocumentoForm': frmDocumentoForm,
#         'lstVariables': lstVariables,
#     }
#     return render(request, 'bases/crear_documento.html', data)
#
#
# @login_required
# def editarDocumentoStandart(request, tdl_id, doc_id):
#     lista_err = []
#     xerror = False
#
#     doc = Documento.objects.get(doc_id=doc_id)
#     frmDocumentoForm = DocumentoGeneralForm(request.POST or None, instance=doc)
#     td = TipoDocumentos.objects.get(tdl_id=tdl_id)
#     if request.POST:
#
#         if frmDocumentoForm.is_valid():
#             form = frmDocumentoForm.save(commit=False)
#             form.tipoDocumentos = td
#             form.save()
#
#             las_bases = BaseEmpresa.objects.all()
#
#             if las_bases.count() > 0:
#
#                 for x in las_bases:
#                     xtd = TipoDocumentos.objects.using(x.ba_conexion).get(tdl_codigo=td.tdl_codigo)
#
#                     d = Documento.objects.using(x.ba_conexion).get(doc_template=doc.doc_template)
#                     d.tipoDocumentos = xtd
#                     d.doc_texto = form.doc_texto
#
#                     d.save(using=x.ba_conexion)
#
#                     html_logo = '{}\n'.format("{% include 'docpdf/style.html' %}")
#                     html_logo += '<table width="100%" border="0" cellspacing="0" cellpadding="0">\n'
#                     html_logo += '<tr>\n'
#                     html_logo += '<td><img class="img-responsive" width="151" height="48" src="{{logo}}"></td>\n'
#                     html_logo += '<td></td>\n'
#                     html_logo += '</tr>\n'
#                     html_logo += '<tr>'
#                     html_logo += '<td colspan="2">\n<br/>\n<br/>\n<br/>\n{}\n</td>\n'.format(form.doc_texto)
#                     html_logo += '</tr>\n'
#                     html_logo += '</table>'
#
#                     ruta_doc = "{}/templates/docpdf/{}".format(BASE_COMMAND, form.doc_template)
#
#                     file = open(ruta_doc, "w")
#                     file.write(html_logo)
#                     file.close()
#
#         else:
#             for field in frmDocumentoForm:
#                 for error in field.errors:
#                     lista_err.append(field.label + ': ' + error)
#             for er in lista_err:
#                 print(er)
#             xerror = True
#
#     frmDocumentoForm.fields['doc_nombre'].widget.attrs['readonly'] = True
#
#     lstVariables = listadoVariableUsuarioEmpesa()
#
#     data = {
#         'error': xerror,
#         'lista_err': lista_err,
#         'tdl_id': tdl_id,
#         'frmDocumentoForm': frmDocumentoForm,
#         'lstVariables': lstVariables,
#     }
#     return render(request, 'bases/crear_documento.html', data)
#
#
# @login_required
# def borrarDocumentoStandart(request, doc_id):
#     la_empresa = BaseEmpresa.objects.all()
#     doc = Documento.objects.get(doc_id=doc_id)
#     for x in la_empresa:
#         xdoc = Documento.objects.using(x.ba_conexion).get(tipoDocumentos__tdl_codigo=doc.tipoDocumentos.tdl_codigo,
#                                                           doc_nombre=doc.doc_nombre)
#         xdoc.delete(using=x.ba_conexion)
#     doc.delete()
#     return redirect('bases:editNuevoTipoDocumento', doc.tipoDocumentos.tdl_id)
