#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from bases.models import BaseEmpresa


class BaseEmpresaForm(ModelForm):
    ba_conexion = forms.CharField(label="Conexión base", widget=forms.TextInput(
        attrs={'class': 'form-control', 'onChange': 'change_conexion()', 'autocomplete': 'off'}))
    ba_name = forms.CharField(label="Nombre de la base",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ba_nameemp = forms.CharField(label="Nombre de la empresa", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': 'autofocus', 'autocomplete': 'off'}))
    ba_esquema = forms.CharField(label="Nombre del esquema",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                 required=False)
    ba_host = forms.CharField(label="Host",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ba_link = forms.CharField(label="Link base", widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': 'readonly', 'autocomplete': 'off'}), required=False)
    ba_fechaingreso = forms.CharField(label="Fecha inicio contrato",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ba_fechatermino = forms.CharField(label="Fecha término de contrato",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    ba_cantidadusuarios = forms.IntegerField(label="Cantidad de usuarios", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}), required=False)

    class Meta:
        model = BaseEmpresa
        fields = [
            'ba_conexion',
            'ba_name',
            'ba_nameemp',
            'ba_host',
            'ba_link',
            'ba_fechaingreso',
            'ba_fechatermino',
            'ba_cantidadusuarios',
        ]


class UserFormBases(UserCreationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off', 'autofocus': 'autofocus'}))
    first_name = forms.CharField(label="Nombres",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    last_name = forms.CharField(label="Apellidos",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    email = forms.EmailField(label="Email",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    password1 = forms.CharField(label="Contraseña",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    password2 = forms.CharField(label="Repite la contraseña",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=140, required=True)
    last_name = forms.CharField(max_length=140, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.DateInput(
        attrs={"class": "form-control", "placeholder": "Nombre usuario", "autofocus": "autofocus",
               "autocomplete": "off"}, ), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Clave"}, ),
                               required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )
