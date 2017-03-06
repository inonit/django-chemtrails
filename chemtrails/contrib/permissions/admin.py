# -*- coding: utf-8 -*-

from django.contrib import admin

from chemtrails.contrib.permissions.models import AccessRule


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    pass

