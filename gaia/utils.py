# -*- encoding: utf-8 -*-
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.shortcuts import render, redirect

import datetime
import time
import locale
import django.conf as conf

from django.contrib.auth.models import User
from bases.forms import BaseEmpresaForm, UserFormBases, LoginForm
from bases.models import BaseEmpresa, ClienteActivo
from seguridad.models import Empresa, Usuario


def elige_choices(obj_choice, str):
    valor = ""
    for key, value in obj_choice:
        if key == str:
            valor = value
    return valor


def load_data_base():
    lista = BaseEmpresa.objects.using('default').all()

    for base in lista:
        domain = base.ba_link
        subdomain = (domain.split('.')[0]).split('//')[1]

        nueva_base = {'ENGINE': conf.settings.DATABASES['default']['ENGINE'], 'HOST': base.ba_host,
                      'NAME': base.ba_name, 'USER': base.ba_user, 'PASSWORD': base.ba_password, 'PORT': base.ba_port}

        conf.settings.DATABASES[subdomain] = nueva_base


# con esta funcion se asignara a un usuario a nivel de session
# de esa manera se podra manejar cualquier dato de usuario
# recibe objeto alumno
def creacionUsuarioSesion(request, user, base):
    try:
        usuario = Usuario.objects.get(user=user)
        usu_tipousuario = usuario.usu_tipousuario
    except:
        usu_tipousuario = ""

    validar_usuario(user, request, base)

    dicUsuario = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'usu_tipousuario': usu_tipousuario,
    }

    request.session["dicUsuario"] = dicUsuario

    # if not base == 'LB':
    #     dataEmpresaSession(request, user.id, user.is_staff)


def dataEmpresaSession(request, id_usuario, is_user_staf=False):
    la_empresa = ""
    razon_social = ""

    if is_user_staf:
        try:
            emp = Empresa.objects.all()
            la_empresa = emp[0].emp_id
            razon_social = emp[0].emp_razonsocial
        except:
            la_empresa = ""
            razon_social = ""
    else:
        user = User.objects.get(id=id_usuario)
        # emp = AsociacionUsuarioEmpresa.objects.filter(user=user)
        # la_empresa = emp[0].empresa.emp_id
        # razon_social = emp[0].empresa.emp_razonsocial

    ca = ClienteActivo.objects.all()

    request.session['la_empresa'] = la_empresa
    request.session['razon_social'] = razon_social
    request.session['cliente_activo'] = ca[0].cac_id
    request.session['x_ruta_imagen'] = "/static/{}/{}".format(ca[0].cac_nombrebase, ca[0].cac_nombreimagenlogo)
    request.session['rutas'] = {
        'cac_rutabase': ca[0].cac_rutabase,
        'cac_rutadocumentos': ca[0].cac_rutadocumentos,
        'cac_rutausuarios': ca[0].cac_rutausuarios,
    }


def obtener_logo_login():
    ca = ClienteActivo.objects.all()
    return "/static/{}/{}".format(ca[0].cac_nombrebase, ca[0].cac_nombreimagenlogo)


def validar_usuario(user, request, base):
    """
    Función que se ejecuta cuando se da pie al logueo de un
    usuario nuevo. Tiene como finalidad almacenar la session_key
    actual del usuario, logrando así, 'desloguear' a otros
    que hayan ingresado con las mismas credenciales
    :param sender:
    :param user:
    :param request:
    :param kwargs:
    :return:
    """

    if request:
        try:
            ## Se agrega esta validación ya que cuando ocurre una autenticación a través de la api
            ## la variable `request.user` es un AnonymousUser y se cambia por la variable `user`
            n_user = request.user.is_anonymous and user or request.user
            ##Se busca un registro acerca de la sesión del usuario
            ##registro = UsuarioLogeado.objects.get(usuario=n_user)
            registro = None
            ##Si nadie ha ingresado antes, se genera el registro del actual usuario en la pagina
            registro.ul_sessionid = request.session.session_key
            registro.save()
        except ObjectDoesNotExist:
            ##En caso de no encontrar el registro se genera uno
            ## ul = UsuarioLogeado()
            ul = None
            ul.usuario = request.user
            ul.ul_sessionid = request.session.session_key
            ul.ul_sistema = base
            ul.save()

    return True


# ************************************************************************************
# ************************************************************************************
def login_user_bases(request):
    """
    Esta funcion carga el templatedel login, y a su vez carga el login de django
    para poder ingresar al sistema
    :param request:
    :return:
    """
    username = request.POST['username']
    password = request.POST['password']

    request.session['error'] = None

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            usuario = Usuario.objects.filter(user=user).last()
            tipo_usuario = ''
            if usuario:
                tipo_usuario = usuario.usu_tipousuario

            dicUsuario = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'tipo_usuario': tipo_usuario,
            }

            request.session["dicUsuario"] = dicUsuario
            return redirect('panel_bases')
        else:
            mensaje = "El usuario no esta activo, porfavor comunicarse con el administrador"
            pagina = 'bases/bases_login.html'
            error = True
    else:
        mensaje = "El usuario no existe"
        pagina = 'bases/bases_login.html'
        error = True

    request.session['error'] = error
    request.session['mensaje'] = mensaje

    return redirect('index_bases')


@login_required(login_url='/login/')
def panel_bases(request):
    """
    Funcion para cerrar sesion, mata las sesiones activas
    :param request:
    :return:
    """
    request.session['tipo_sistema'] = 'bases'
    return render(request, 'bases/base.html', {})


def index_bases(request):
    """
    :param request:
    :return: pagina de logeo
    """

    data = {
        'form': LoginForm,
    }
    return render(request, 'bases/bases_login.html', data)

# ************************************************************************************
# ************************************************************************************
