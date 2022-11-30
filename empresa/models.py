from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

# Create your models here.
from seguridad.models import Empresa, Sucursal


class AsociacionUsuarioEmpresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    aue_id = models.AutoField("Key", primary_key=True)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="aue_usuario", on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="aue_empresa", on_delete=models.PROTECT)
    sucursal = models.ForeignKey(Sucursal, verbose_name="Sucursal", db_column="aue_sucursal", null=True, blank=True, on_delete=models.PROTECT)
    aue_activo = models.CharField("Personal activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.aue_id

    def __str__(self):
        return "{}".format(self.aue_id)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(AsociacionUsuarioEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_asociacion_usuario_empresa'
        ordering = ['aue_id']


class AsociacionUsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = ('aue_id', 'user', 'empresa', 'sucursal')

