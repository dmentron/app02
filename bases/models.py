#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin


# Create your models here.
class BaseEmpresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )
    ENGINE = (
        ('P', 'django.db.backends.postgresql_psycopg2'),
    )

    ba_id = models.AutoField("Key", primary_key=True)
    ba_conexion = models.CharField("ALIAS", max_length=255)
    ba_engine = models.CharField("ENGINE", max_length=255, choices=OPCIONES, default="P")
    ba_esquema = models.CharField("'options': '-c search_path='", max_length=255, null=True, blank=True)
    ba_name = models.CharField("NAME", max_length=255)
    ba_user = models.CharField("USER", max_length=255, default='osbustaman')
    ba_password = models.CharField("PASSWORD", max_length=255, default='16090942')
    ba_host = models.CharField("HOST", max_length=255, default='localhost')
    ba_port = models.CharField("PORT", max_length=255, default='5432')
    ba_nameemp = models.CharField("Nombre de la empresa", max_length=255)
    ba_activa = models.CharField("Base activa", max_length=1, choices=OPCIONES, default="N")
    ba_fechaingreso = models.DateField("Fecha creación de la base", null=True, blank=True)
    ba_fechatermino = models.DateField(verbose_name='Fecha termino de la base', null=True, blank=True)
    ba_link = models.CharField("Link base", max_length=255, default='')
    ba_adddprc = models.CharField("Parametros generales (pais, región, comuna, etc.)", max_length=1, choices=OPCIONES, default="N")
    ba_additm = models.CharField("Creacion de menu", max_length=1, choices=OPCIONES, default="N")
    ba_armada = models.CharField("Estuctura de la base armada", max_length=1, choices=OPCIONES, default="N")
    ba_creada = models.CharField("Base creada", max_length=1, choices=OPCIONES, default="N")
    ba_idclienteactivo = models.IntegerField("ID base cliente activo", null=True, blank=True)
    ba_cantidadusuarios = models.IntegerField("Cantidad usuarios", null=True, blank=True)

    def __int__(self):
        return self.ba_id

    def __str__(self):
        return "{n}".format(n=self.ba_name.title())

    def __migrate(self):
        return "migrate --database {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    el_migrate = property(__migrate)

    def __config_data_generic(self):
        return "config_data_generic {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_data_generic = property(__config_data_generic)

    def __config_ruta(self):
        return "login/empresa/{NOMBRE_BASE_DE_DATOS}/".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_ruta = property(__config_ruta)

    def __config_super_user(self):
        return "createsuperuser --database {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_super_user = property(__config_super_user)

    def save(self, *args, **kwargs):
        self.ba_conexion = self.ba_conexion.lower()
        self.ba_esquema = self.ba_esquema.lower()
        self.ba_name = self.ba_name.lower()
        self.ba_nameemp = self.ba_nameemp.lower()
        self.ba_link = self.ba_link.lower()
        super(BaseEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'bases_bases'
        ordering = ['ba_id']


class BaseEmpresaAdmin(admin.ModelAdmin):
    list_display = ('ba_id', 'ba_nameemp', 'ba_name', 'ba_password', 'ba_host', 'ba_port', 'ba_activa', 'el_migrate')


class ClienteActivo(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    cac_id = models.AutoField("Key", primary_key=True)
    cac_activo = models.CharField("Cliente activo?", max_length=1, choices=OPCIONES, default="S")
    cac_cantempleados = models.IntegerField("Cantidad de empleados", null=True, blank=True, default=10)
    cac_rutabase = models.CharField("Ruta base", max_length=255, null=True, blank=True, default='')
    cac_rutadocumentos = models.CharField("Ruta documentos", max_length=255, null=True, blank=True, default='')
    cac_rutadstatic = models.CharField("Ruta archivos static", max_length=255, null=True, blank=True, default='')
    cac_rutausuarios = models.CharField("Ruta usuarios", max_length=255, null=True, blank=True, default='')
    cac_nombrebase = models.CharField("Nombre base", max_length=255, null=True, blank=True, default='')
    cac_nombreimagenlogo = models.CharField("Nombre imagen logo", max_length=255, null=True, blank=True, default='')

    def __int__(self):
        return self.cac_id

    def __str__(self):
        return "{n}".format(n=self.cac_id)

    def __ruta_documentos_completa__(self):
        return "/{}/{}/".format(self.cac_rutabase, self.cac_rutadocumentos)

    ruta_base = property(__ruta_documentos_completa__)

    def __ruta_usuarios_completa__(self):
        return "/{}/{}/".format(self.cac_rutabase, self.cac_rutausuarios)

    ruta_usuarios = property(__ruta_usuarios_completa__)

    def save(self, *args, **kwargs):
        super(ClienteActivo, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_cliente_activo"
        ordering = ['cac_id']


class ClienteActivoAdmin(admin.ModelAdmin):
    list_display = ('cac_activo', 'cac_activo')


# --------------------------------------------------------------
class Parametros(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    param_id = models.AutoField("Key", primary_key=True)
    param_codigo = models.CharField("Código del parámetro", max_length=10)
    param_descripcion = models.TextField("Descripción", max_length=255)
    param_valor = models.CharField("Valor", max_length=50, null=True, blank=True, default=0)
    param_rangoini = models.DecimalField("Desde $", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    param_rangofin = models.DecimalField("Hasta $", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    param_factor = models.CharField("Factor", max_length=50)
    param_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.param_id

    def __str__(self):
        return "{n}-{cc}".format(n=self.param_id, cc=self.param_descripcion)

    def save(self, *args, **kwargs):
        super(Parametros, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_parametros"
        ordering = ['param_id']


class ParametrosAdmin(admin.ModelAdmin):
    list_display = (
    'param_id', 'param_codigo', 'param_descripcion', 'param_valor', 'param_rangoini', 'param_rangofin', 'param_activo')


class TablaGeneral(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    tg_id = models.AutoField(primary_key=True)
    tg_nomtabla = models.CharField("Nombre tabla", max_length=255)
    tg_codigo = models.CharField("Código", max_length=15)
    tg_cod_ext = models.CharField("Código externo", blank=True, null=True, default='', max_length=15)
    tg_descripcion = models.CharField("Descripción", max_length=150)
    tg_num_aux = models.IntegerField("Número auxiliar", blank=True, null=True)
    tg_fecha_aux = models.DateField("Fecha auxiliar", blank=True, null=True)
    tg_text_aux = models.CharField("Texto auxiliar", max_length=200, blank=True, null=True)
    tg_valor = models.DecimalField("Valor", max_digits=15, decimal_places=2, blank=True, null=True)
    # user_cre = models.IntegerField(verbose_name='Usuario Creador', default=0)
    # fecha_cre = models.DateTimeField(verbose_name='Fecha Creacion', default=timezone.now)
    # user_mod = models.IntegerField(verbose_name='Usuario Modificador', default=0)
    # fecha_mod = models.DateTimeField(verbose_name='Fecha Modificacion', default=timezone.now)
    tg_estado = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.tg_id

    def __str__(self):
        return "{}-{}".format(self.tg_codigo, self.tg_descripcion)

    def save(self, *args, **kwargs):
        super(TablaGeneral, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_tabla_general"
        ordering = ['tg_id']


class TablaGeneralAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'tg_nomtabla', 'tg_codigo', 'tg_descripcion', 'tg_estado')

