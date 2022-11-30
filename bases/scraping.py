# -*- encoding: utf-8 -*-
import datetime
import json
import os
import argparse
import urllib.request
import wget

from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from gaia.settings import PORT_LOCALHOST, NAME_HOST, STATICFILES_DIRS

@login_required
@csrf_exempt
def armar_page(request):

    if request.POST:

        datos = urllib.request.urlopen(str(request.POST['x_page'])).read().decode()
        soup = BeautifulSoup(datos, features='lxml')

        ultimo_elemento = (request.POST['x_page']).split('/')
        x_http = ultimo_elemento[0]

        ruta_0 = ''
        for x in range(2, len(ultimo_elemento)-1):
            ruta_0+=ultimo_elemento[x]+'/'

        directorio_static = STATICFILES_DIRS[0]+'/scraping/'+ruta_0
        try:
            os.makedirs(directorio_static)
        except FileExistsError:
            pass
        except:
            pass

        f = open(directorio_static+str(ultimo_elemento[-1]), 'w')
        x_html = str(soup)
        f.write(x_html)
        f.close()

        request.session['host_name'] = ultimo_elemento[0]+'//'+ultimo_elemento[1]+ultimo_elemento[2]

        listado_css = scrap_html(soup('link'), 'href', directorio_static, x_http)
        listado_img = scrap_html(soup('img'), 'src', directorio_static, x_http)
        listado_js = scrap_html(soup('script'), 'src', directorio_static, x_http)
        print("La fuente fue descargada exitosamente!!!")

    html = {
        'host_name': request.session['host_name'] + '#: HTML creado con éxito',
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


def scrap_html(tag_soup, x_type, dir_st, x_http):
    lst_type = []
    tags = tag_soup
    for tag in tags:
        t = (tag.get(x_type)).split("/")
        # print(dir_st, ' - - - ', t)
        # print(tag.get(x_type))
        x_url = ''
        cant = t.count('..')
        for x in t:
            if not x == '..':
                x_url += '/'+x

        x_url_2 = ''
        x_dir_st = dir_st.split('/')
        for y in x_dir_st:
            if not y == '':
                x_url_2 += '/'+y

        final_url = ''
        lst_url = x_url_2.split('/')
        for x in range(0, len(lst_url)-cant):
            final_url += '/'+lst_url[x]

        final_url_base = final_url.replace('//', '/')+'/'
        final_url = (final_url_base+x_url).replace('//', '/')
        x_ruta = x_http+'//'+(final_url.split('/scraping/'))[1]

        url_0 = x_ruta
        path_0 = final_url

        path_os = path_0.split('/')
        path_string = ''
        for x in range(0, len(path_os)-1):
            path_string += path_os[x]+'/'

        try:
            os.makedirs(path_string)
        except FileExistsError:
            os.scandir(path_string)
        except:
            pass

        print(url_0, '  ---->  ', path_0)
        try:
            wget.download(url_0, path_0)
        except:
            pass
        lst_type.append(url_0 + '  ---->  ' + path_0)


    return lst_type


