from django.urls import path

from . import views, scraping

urlpatterns = [

    path('login/', views.bases_login, name='login'),
    path('listado/', views.listado_bases, name='listado_bases'),

    path('editar/base/<int:id_base>/', views.editar_base, name='editar_base'),
    path('create/database/', views.create_database, name='create_database'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/base/datos/', views.add_base_de_datos, name='add_base_de_datos'),
    path('armar/estructura/carpeta/empresa/', views.armar_estructura_carpeta_empresa, name='armar_estructura_carpeta_empresa'),

    path('armar/intruccion/', views.armar_instruccion, name='armar_instruccion'),
    path('web/scraping/', views.web_scraping, name='web_scraping'),
    path('armar/page/', scraping.armar_page, name='armar_page'),
]
