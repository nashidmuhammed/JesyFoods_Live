from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import *
from import_export.admin import ImportExportModelAdmin


@admin.register(Products)
class prodat(ImportExportModelAdmin):
    pass


@admin.register(Party)
class userdat(ImportExportModelAdmin):
    pass


class ForParty(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = Party


class saleItem(ImportExportModelAdmin):
    resource_class = ForParty
    pass


class ForWid(resources.ModelResource):
    id_prefix = fields.Field(
        column_name='id_prefix',
        attribute='id_prefix',
        widget=ForeignKeyWidget(Prefix, 'prefix')
    )
    party_name = fields.Field(
        column_name='party_name',
        attribute='party_name',
        widget=ForeignKeyWidget(Party, 'party_name')
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = Sale


class ForWidItm(resources.ModelResource):
    iid = fields.Field(
        column_name='iid',
        attribute='iid',
        widget=ForeignKeyWidget(Sale, 'iid')
    )
    party_name = fields.Field(
        column_name='party_name',
        attribute='party_name',
        widget=ForeignKeyWidget(Party, 'party_name')
    )
    p_name = fields.Field(
        column_name='p_name',
        attribute='p_name',
        widget=ForeignKeyWidget(Products, 'pname')
    )

    class Meta:
        model = Sale_item


class saledata(ImportExportModelAdmin):
    resource_class = ForWid
    pass


class saleItem(ImportExportModelAdmin):
    resource_class = ForWidItm
    pass


# admin.site.register(Party),
# admin.site.register(Products),
admin.site.register(Sale, saledata),
admin.site.register(Sale_item, saleItem),
admin.site.register(Prefix),
admin.site.register(Profile),
admin.site.register(Report),
admin.site.register(Messages),
admin.site.register(Expense),
admin.site.register(Collection),
admin.site.register(Settings),
admin.site.register(Alert),
admin.site.register(DataInfo),
