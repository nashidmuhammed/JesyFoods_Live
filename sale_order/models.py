import datetime

from django.contrib.auth.models import User
from django.db import models

USAGE = (
    ('order', 'order'),
    ('sale', 'sale'),
    ('return', 'return'),
    ('payment', 'payment')
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, default='Staff')
    balance = models.FloatField(default=0)
    date_created = models.DateTimeField(auto_now=True, null=True)
    salary = models.CharField(max_length=50, blank=True)
    phone_2 = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    gpay = models.CharField(max_length=50, blank=True, null=True)
    account = models.CharField(max_length=100, blank=True)
    ifsc = models.CharField(max_length=50, blank=True)
    branch = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.user)


class Products(models.Model):
    pname = models.CharField(max_length=100, unique=True)
    size = models.CharField(max_length=100)
    r_price = models.FloatField()
    w_price = models.FloatField()
    h_price = models.FloatField()
    d_price = models.FloatField()
    HSN = models.FloatField(default=0)
    mrp = models.FloatField()
    barcode = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.pname


class Party(models.Model):
    TYPE = (
        ('Retail', 'Retail'),
        ('Wholesale', 'Wholesale'),
        ('Hotel', 'Hotel'),
        ('Distribution', 'Distribution'),
    )
    CATEGORY = (
        ('Grocery', 'Grocery'),
        ('Supermarket', 'Supermarket'),
        ('Vegetables', 'Vegetables'),
        ('Hotel', 'Hotel'),
    )
    PartyType = (
        ('seller','seller'),
        ('buyer', 'buyer'),
        ('both', 'both'),
    )
    party_name = models.CharField(max_length=100, unique=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    GSTIN = models.CharField(max_length=100, null=True, blank=True)
    owner = models.CharField(max_length=100, blank=True)
    account = models.TextField(max_length=500, null=True, blank=True)
    email = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY, default='Grocery')
    type = models.CharField(max_length=100, choices=TYPE, default='Retail')
    created = models.DateTimeField(auto_now_add=True)
    balance = models.FloatField(default=0)
    route = models.CharField(max_length=100, default='General')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField( default="shope_profile.jpg")
    party_type = models.CharField(max_length=15, default='seller',choices=PartyType)
    party_group = models.CharField(max_length=20, default='fasal')

    def __str__(self):
        return str(self.party_name)


class Prefix(models.Model):
    prefix = models.CharField(max_length=15, null=True, unique=True)
    last_id = models.IntegerField(default=0)
    used = models.CharField(max_length=100, choices=USAGE)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.prefix)


class Sale(models.Model):
    TYPE = (
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Gpay', 'Gpay'),
    )
    s_id = models.IntegerField(default=0)
    id_prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, null=True)
    iid = models.CharField(max_length=100, unique=True)
    party_name = models.ForeignKey(Party, on_delete=models.CASCADE, null=True)
    party_type = models.CharField(max_length=100, default='Retail')
    date = models.DateTimeField(null=True)
    t_type = models.CharField(max_length=100, choices=USAGE)
    total = models.FloatField(default=0)
    t_total = models.FloatField(max_length=25, default=0)
    q_total = models.FloatField(max_length=25, default=0)
    fq_total = models.FloatField(max_length=25, default=0)
    received = models.FloatField(max_length=25, default=0)
    p_type = models.CharField(max_length=10, choices=TYPE, default='Cash')
    balance = models.FloatField(max_length=25, null=True)
    report = models.TextField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, )
    ir_date = models.DateTimeField(blank=True, null=True,)
    ir_iid = models.CharField(max_length=50, blank=True, null=True,)

    def __str__(self):
        return str(self.iid)


class Sale_item(models.Model):
    iid = models.ForeignKey(Sale, on_delete=models.CASCADE)
    party_name = models.ForeignKey(Party, on_delete=models.CASCADE)
    p_name = models.ForeignKey(Products, on_delete=models.CASCADE)
    price = models.FloatField(null=True)
    t_price = models.FloatField(null=True)
    gst = models.FloatField(null=True)
    qty = models.FloatField(null=True)
    fqty = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    t_amount = models.FloatField(default=0)

    def __str__(self):
        return str(self.iid)


# class Return(models.Model):
#     i_date = models.DateTimeField(null=True)
#     i_iid = models.CharField(max_length=50)
#     iid = models.ForeignKey(Sale, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return str(self.iid)


class Report(models.Model):
    date = models.DateTimeField(auto_now=True)
    party_name = models.ForeignKey(Party, on_delete=models.CASCADE)
    report = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default='report')
    disc = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.party_name)


class Messages(models.Model):
    date = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=200, default='General')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    msg = models.TextField(max_length=500)

    def __str__(self):
        return str(self.name)


class Expense(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense = models.CharField(max_length=100)
    amount = models.FloatField()
    disc = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Collection(models.Model):
    date = models.DateTimeField(default=datetime.datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    p_type = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    amount = models.FloatField()

    def __str__(self):
        return str(self.user)


class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_order = models.BooleanField(default=True)
    home_daybook = models.BooleanField(default=True)
    home_sale = models.BooleanField(default=True)
    home_credit = models.BooleanField(default=False)
    home_expense = models.BooleanField(default=True)
    inv_view_tax = models.BooleanField(default=True)
    inv_view_round = models.BooleanField(default=True)
    inv_pdf_tax = models.BooleanField(default=True)
    inv_pdf_round = models.BooleanField(default=True)
    inv_pdf_balance = models.BooleanField(default=False)
    inv_pdf_column = models.IntegerField(default=10)

    def __str__(self):
        return str(self.user)


class Log(models.Model):
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, )
    type = models.CharField(max_length=200, default='Information')
    process = models.CharField(max_length=200)
    reference = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.date)


class Alert(models.Model):
    date = models.DateTimeField(auto_now=True)
    heading = models.CharField(max_length=200)
    body = models.TextField(max_length=500)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, )
    
class DataInfo(models.Model):
    date = models.DateTimeField(auto_now=True)
    prev_date = models.DateTimeField(null=True,blank=True)
    ip = models.CharField(max_length=20 , null=True,blank=True)
    hostname = models.CharField(max_length=100, null=True,blank=True)
    visited = models.FloatField(default=1)
    details = models.TextField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return str(self.hostname)