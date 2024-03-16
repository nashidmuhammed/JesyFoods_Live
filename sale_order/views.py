from datetime import datetime
import os
import sys      
import socket

from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from num2words import num2words
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .forms import CreateUserForm
from django.db.models import Max, Q, F,Case, When, Value, IntegerField

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users



from .models import *


def index(request):
    try:
        if request.GET.get('debug') is not None:  
            details = request.GET.get('debug')
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # if DataInfo.objects.filter(ip=ip).exists():
            #     info = DataInfo.objects.get(ip=ip)
            #     info.prev_date = info.date
            #     info.hostname = hostname
            #     info.visited += 1
            #     info.details = str('From Index\n\n') + str(details) 
            #     info.save()
            # else:
            DataInfo.objects.create(
                ip = ip,
                hostname = hostname,
                details = str('From Index\n\n') + str(details)
            )
    except:
        pass    
    return render(request, 'jesyfoods-main/index.html')


def products(request):
    return render(request, 'jesyfoods-main/products.html')


def about(request):
    return render(request, 'jesyfoods-main/about.html')


def contact(request):
    try:
        if request.method == 'POST':
            if request.POST['name'] == 'Gosedext':
                messages.success(request, 'Sorry :( ')
            else:
                
                details = request.GET.get('debug')
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                # if DataInfo.objects.filter(ip=ip).exists():
                #     info = DataInfo.objects.get(ip=ip)
                #     info.prev_date = info.date
                #     info.hostname = hostname
                #     info.visited += float(0.1)
                #     info.details = str('From Contact\n\n') + str(details) 
                #     info.save()
                # else:
                DataInfo.objects.create(
                    ip = ip,
                    hostname = hostname,
                    details = str('From Contact\n\n') + str(details)
                )
                Messages.objects.create(
                    type=request.POST['category'],
                    name=request.POST['name'],
                    phone=request.POST['phone'],
                    email=request.POST['email'],
                    msg=request.POST['message']
                )
                messages.success(request, 'Form submitted successfully ')
            Log.objects.create(process=request.POST['category'], reference=request.POST['name'])  # Log_added
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='contact',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'jesyfoods-main/contact.html')


def faq(request):
    return render(request, 'jesyfoods-main/faq.html')


def tasty_hub(request):
    return render(request, 'jesyfoods-main/tasty_hub.html')


# ADMIN SECTION
@unauthenticated_user
def loginPage(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect')
        context = {}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='LoginPage',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@allowed_users(allowed_roles=['admin'])
def registerPage(request):
    try:
        with transaction.atomic():
            form = CreateUserForm()
            if request.method == 'POST':
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    username = form.cleaned_data.get('username')

                    group = Group.objects.get(name='staff')
                    user.groups.add(group)
                    Profile.objects.create(
                        user=user,
                    )
                    Settings.objects.create(
                        user=user,
                    )

                    messages.success(request, 'Account was created for ' + username)
                    Log.objects.create(user=request.user, process='Register User', reference=username)  # Log_added
                    return redirect('login')
            context = {'form': form}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='registerPage',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'register.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admin_panel(request):
    try:
        now = timezone.now()
        year = now.year
        r_sale = Sale.objects.all().order_by('-date')[:20]
        odr = Sale.objects.filter(t_type='order')
        count = odr.count()
        count_msg = Messages.objects.all().count()
        cr = 0
        p = Party.objects.all()
        for i in p:
            cr += i.balance
        coll_tot = 0
        day_coll = Sale.objects.filter(date__date__gte=timezone.now().date())
        for i in day_coll:
            coll_tot += i.received
        tot_sale = 0
        day_sale = Sale.objects.filter(t_type='sale', date__date__gte=timezone.now().date())
        for i in day_sale:
            tot_sale += i.total
        sd = datetime.datetime(now.year, now.month, 1).date()
        # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(days=2)
        # ed=sd
        # ed = ed.date()
        dt = datetime.datetime(now.year, now.month, 1)
        ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
        month_sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed])
        month_tot = 0
        for i in month_sale:
            month_tot += i.total
        # psd = datetime.datetime(now.year, now.month - 1, 1).date()
        psd = datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)
        ped = datetime.datetime(now.year, now.month, 2) - datetime.timedelta(days=2)
        ped = ped.date()
        prev_sale = Sale.objects.filter(t_type='sale', date__date__range=[psd, ped])
        prev_tot = 0
        for i in prev_sale:
            prev_tot += i.total
        exp = 0
        ex = Expense.objects.filter(date__date__gt=sd, date__date__lt=ed)
        for i in ex:
            exp += i.amount
        td_exp = 0
        ex = Expense.objects.filter(date__date__gte=timezone.now().date())
        for i in ex:
            td_exp += i.amount

        # barChart
        m0_sale = 0
        m0 = now.month
        m0_text = datetime.datetime.now().strftime('%B')
        sale = Sale.objects.filter(t_type='sale', date__year=year, date__month=m0)
        for i in sale:
            m0_sale += i.total
        print('mo =', m0)
        # m1 = datetime.datetime(now.year, now.month - 1, 1).month
        m11 = datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)
        # m1_text = datetime.datetime(now.year, now.month - 1, 1).strftime('%B')
        m1_text = m11.strftime('%B')
        m1 = m11.month
        m1_sale = 0
        sale = Sale.objects.filter(t_type='sale', date__year=m11.year, date__month=m1)
        for i in sale:
            m1_sale += i.total

        # m2 = datetime.datetime(now.year, now.month - 2, 1).month
        m22 = datetime.datetime(now.year, now.month, 1) - relativedelta(months=2)
        # m2_text = datetime.datetime(now.year, now.month - 2, 1).strftime('%B')
        m2_text = m22.strftime('%B')
        m2_sale = 0
        m2 = m22.month
        sale = Sale.objects.filter(t_type='sale', date__year=m22.year, date__month=m2)
        for i in sale:
            m2_sale += i.total

        # m3 = datetime.datetime(now.year, now.month - 3, 1).month
        m33 = datetime.datetime(now.year, now.month, 1) - relativedelta(months=3)
        # m3_text = datetime.datetime(now.year, now.month - 3, 1).strftime('%B')
        m3_text = m33.strftime('%B')
        m3_sale = 0
        m3 = m33.month
        sale = Sale.objects.filter(t_type='sale', date__year=m33.year, date__month=m3)
        for i in sale:
            m3_sale += i.total

        # m4 = datetime.datetime(now.year, now.month - 4, 1).month
        m44 = datetime.datetime(now.year, now.month, 1) - relativedelta(months=4)
        # m4_text = datetime.datetime(now.year, now.month - 4, 1).strftime('%B')
        m4_text = m44.strftime('%B')
        m4_sale = 0
        m4 = m44.month
        sale = Sale.objects.filter(t_type='sale', date__year=m44.year, date__month=m4)
        for i in sale:
            m4_sale += i.total

        # WEEKS

        w1 = 0
        w1_d = datetime.datetime(now.year, now.month, 1).date().strftime('%V')
        sale = Sale.objects.filter(t_type='sale', date__year=year, date__week=w1_d)
        for i in sale:
            w1 += i.total

        w2 = 0
        w2_d = float(w1_d) + 1
        sale = Sale.objects.filter(t_type='sale', date__year=year, date__week=w2_d)
        for i in sale:
            w2 += i.total

        w3 = 0
        w3_d = w2_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=year, date__week=w3_d)
        for i in sale:
            w3 += i.total

        w4 = 0
        w4_d = w3_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=year, date__week=w4_d)
        for i in sale:
            w4 += i.total

        w11 = 0
        # w11_d = datetime.datetime(now.year, now.month - 1, 1).date().strftime('%V')
        w11_dd = datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)
        w11_d = w11_dd.date().strftime('%V')
        print("w11_dd===>",w11_dd)
        print("w11_d===>",w11_d)
        sale = Sale.objects.filter(t_type='sale', date__year=w11_dd.year, date__week=w11_d)
        for i in sale:
            w11 += i.total
        w22 = 0
        w22_d = float(w11_d) + 1
        print("w22_d===>",w22_d)
        
        sale = Sale.objects.filter(t_type='sale', date__year=w11_dd.year, date__week=w22_d)
        for i in sale:
            w22 += i.total
        w33 = 0
        w33_d = w22_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=w11_dd.year, date__week=w33_d)
        for i in sale:
            w33 += i.total
        w44 = 0
        w44_d = w33_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=w11_dd.year, date__week=w44_d)
        for i in sale:
            w44 += i.total

        w111 = 0
        # w111_d = datetime.datetime(now.year, now.month - 2, 1).date().strftime('%V')
        w111_dd = datetime.datetime(now.year, now.month, 1) - relativedelta(months=2)
        w111_d = w111_dd.date().strftime('%V')
        print("w111_d===>",w111_d)
        
        sale = Sale.objects.filter(t_type='sale', date__year=w111_dd.year, date__week=w111_d)
        for i in sale:
            w111 += i.total
        w222 = 0
        w222_d = float(w111_d) + 1
        sale = Sale.objects.filter(t_type='sale', date__year=w111_dd.year, date__week=w222_d)
        for i in sale:
            w222 += i.total
        w333 = 0
        w333_d = w222_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=w111_dd.year, date__week=w333_d)
        for i in sale:
            w333 += i.total
        w444 = 0
        w444_d = w333_d + 1
        sale = Sale.objects.filter(t_type='sale', date__year=w111_dd.year, date__week=w444_d)
        for i in sale:
            w444 += i.total

        # Top Products
        list_sale = list(Sale.objects.filter(t_type='sale', date__date__range=[sd, ed.date()]).values_list('iid', flat=True))
        top_selling = Sale_item.objects.filter(iid__iid__in=list_sale).values('p_name__pname').annotate(
            total_qty=Sum(
                Case(
                    When(p_name__size='50g', then=F('qty') / 20),
                    When(p_name__size='100g', then=F('qty') / 10),
                    When(p_name__size='250g', then=F('qty') / 4),
                    When(p_name__size='500g', then=F('qty') / 2),
                    default=F('qty'),
                    output_field=IntegerField()
                )
            ), total_amount=Sum(F('qty') * F('price'))).order_by('-total_qty')[:10]
        
        # Top Customers
        top_customer = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed.date()]).values('party_name__party_name').annotate(total_sales=Sum('total'),total_received=Sum('received')).order_by('-total_sales')[:10]


        context = {'labels': [m4_text, m3_text, m2_text, m1_text, m0_text],
                'data': [m4_sale, m3_sale, m2_sale, m1_sale, m0_sale],
                'weeks': [w1, w2, w3, w4],
                'weeks2': [w11, w22, w33, w44],
                'weeks3': [w111, w222, w333, w444],
                'prev1_month': str(m2_text),
                'top_selling':top_selling,
                'top_customer':top_customer,
                }
        print("context =", context)
        return render(request, 'adm/admin_panel.html',
                    {'sale': r_sale, 'count': count, 'tot_sale': tot_sale, 'coll_tot': coll_tot, 'month_tot': month_tot,
                    'prev_tot': prev_tot, 'this_month': sd, 'month_end': ed, 'cr': cr, 'exp': exp,
                    'td_exp': td_exp, 'context': context, 'count_msg': count_msg})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='admin_panel',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def sale_report(request):
    try:
        flt = 'today'
        sr = None
        if request.method == 'POST':
            sr = request.POST['search']
            all = request.POST.get('all')
            print("all====>",all)
            sd = None
            ed = timezone.now().date() + datetime.timedelta(days=1)
            flt = 'date'
            sale = Sale.objects.filter(t_type='sale', iid__icontains=sr) | Sale.objects.filter(
                t_type='sale', party_name__party_name__icontains=sr).order_by('-date')
        else:
            sd = timezone.now().date()
            ed = timezone.now().date() + datetime.timedelta(days=1)
            sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('-date')
            ed = sd
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='sale_report',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'adm/adm_sale_report.html',
                  {'sale': sale, 'sd': sd, 'ed': ed, 'flt': flt, 'total': total, 'no': no, 'sr': sr})


def sale_report_filter(request):
    try:
        flt = request.POST['filter']
        now = timezone.now()
        if flt == 'yesterday':
            sd = timezone.now().date() - datetime.timedelta(days=1)
            ed = sd
            sale = Sale.objects.filter(t_type='sale', date__date=sd).order_by('date')
        elif flt == 'This Month':
            sd = datetime.datetime(now.year, now.month, 1).date()
            # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(days=2)
            # ed = ed.date()
            dt = datetime.datetime(now.year, now.month, 1)
            ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)

            sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('date')
        elif flt == 'Prev Month':
            # sd = datetime.datetime(now.year, now.month - 1, 1).date()
            sd = (datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)).date()
            ed = datetime.datetime(now.year, now.month, 2) - datetime.timedelta(days=2)
            ed = ed.date()
            print('sd =',sd)
            print('ed =',ed)
            sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('date')
            # sale = Sale.objects.filter(t_type='sale', date__date__lte=ed, date__date__gte=sd).order_by('date')
        elif flt == 'This Year':
            sd = datetime.datetime(now.year, 1, 1)
            ed = datetime.datetime.today()
            sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('date')
        else:
            return redirect('sale_report')
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
        print('sd =',sd)
        print('ed =',ed)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='sale_report_filter',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'adm/adm_sale_report.html',
                  {'sale': sale, 'sd': sd, 'ed': ed, 'flt': flt, 'total': total, 'no': no})


def sale_report_date(request):
    try:
        flt = 'date'
        if request.POST.get('sd') == '' or request.POST.get('ed') == '':
            return redirect('sale_report')
        sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
        ed = datetime.datetime.strptime(request.POST['ed'], "%Y-%m-%d").date()
        sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('date')
        # ed = ed - datetime.timedelta(days=1)
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='sale_report_date',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    return render(request, 'adm/adm_sale_report.html',
                  {'sale': sale, 'sd': sd, 'ed': ed, 'flt': flt, 'total': total, 'no': no})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def sale_report_new(request):    
    if request.method == 'POST':
        print("searcheeeeeeeeeeee")
        sr = request.POST['search']
        sd = request.POST['sd']
        ed = request.POST['ed']
        flt = request.POST['filter']
        retail = request.POST.get('retail')
        hotel = request.POST.get('hotel')
        wholesale = request.POST.get('wholesale')
        distribution = request.POST.get('distribution')
        general = request.POST.get('general')
        print("sd===>",sd)
        print("ed===>",ed)
        print("general===>",general)
        sale = Sale.objects.filter(t_type='sale', date__date__gte=sd, date__date__lte=ed).order_by('-date')
        if retail and hotel and wholesale and distribution and general:
            all = True
        else:
            all = False
        p_types = []
        if retail:
            # sale = sale.filter(party_type="Retail")
            p_types.append("Retail")
            retail = True
        if hotel:
            # sale = sale.filter(party_type="Hotel")
            p_types.append("Hotel")
            hotel = True
        if wholesale:
            p_types.append("Wholesale")
            # sale = sale.filter(party_type="Wholesale")
            wholesale = True
        if distribution:
            p_types.append("Distribution")
            # sale = sale.filter(party_type="Distribution")
            distribution = True
        if general:
            p_types.append("General")
            # sale = sale.filter(party_type="General")
            general = True
        sale = sale.filter(party_type__in=p_types)
    else:   
        sd = datetime.datetime.today().strftime('%Y-%m-%d')
        # ed = timezone.now().date() + datetime.timedelta(days=1)
        ed = sd
        all =True
        retail = True
        hotel = True
        wholesale = True
        distribution = True
        general = True
        flt = "today"
        total = 0
        no = 0
        sr = None
        sale = Sale.objects.filter(t_type='sale', date__date__gte=sd, date__date__lte=ed).order_by('-date')
    total = sale.aggregate(Sum('total'))['total__sum']
    no = sale.count()
    print("sale===>",sale)
    print("sr===>",sr)
    print("sd===>",sd)
    print("ed===>",ed)
    return render(request, 'adm/adm_sale_report_new.html',
                  {'sale': sale, 'sd': sd, 'ed': ed, 'flt': flt, 'total': total, 'no': no, 'sr': sr,
                   'all':all,'retail':retail,'hotel':hotel,'wholesale':wholesale,'distribution':distribution,'general':general})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def payments(request):
    sd = timezone.now().date()
    ed = timezone.now().date() + datetime.timedelta(days=1)
    sale = Sale.objects.filter(t_type='payment', date__date__range=[sd, ed]).order_by('-date')
    return render(request, 'adm/adm_payments.html', {'sale': sale, 'sd': sd, 'ed': ed})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def payments_new(request):
    if request.method == 'POST':
        print("searcheeeeeeeeeeee")
        sr = request.POST['search']
        group = request.POST['group']
        sd = request.POST['sd']
        ed = request.POST['ed']
        flt = request.POST['filter']
        retail = request.POST.get('retail')
        hotel = request.POST.get('hotel')
        wholesale = request.POST.get('wholesale')
        distribution = request.POST.get('distribution')
        general = request.POST.get('general')
        print("sd===>",sd)
        print("ed===>",ed)
        print("general===>",general)
        t_type = ['payment','sale']
        if group == 'all':
            sale = Sale.objects.filter(t_type__in=t_type, date__date__gte=sd, date__date__lte=ed).order_by('-date')
        else:
            
            sale = Sale.objects.filter(party_name__party_group=group,t_type__in=t_type, date__date__gte=sd, date__date__lte=ed).order_by('-date')
            
        if retail and hotel and wholesale and distribution and general:
            all = True
        else:
            all = False
        p_types = []
        if retail:
            # sale = sale.filter(party_type="Retail")
            p_types.append("Retail")
            retail = True
        if hotel:
            # sale = sale.filter(party_type="Hotel")
            p_types.append("Hotel")
            hotel = True
        if wholesale:
            p_types.append("Wholesale")
            # sale = sale.filter(party_type="Wholesale")
            wholesale = True
        if distribution:
            p_types.append("Distribution")
            # sale = sale.filter(party_type="Distribution")
            distribution = True
        if general:
            p_types.append("General")
            # sale = sale.filter(party_type="General")
            general = True
        print("sales============>",sale)
        sale = sale.filter(party_type__in=p_types)
    else:   
        sd = datetime.datetime.today().strftime('%Y-%m-%d')
        # ed = timezone.now().date() + datetime.timedelta(days=1)
        group = 'all'
        ed = sd
        all =True
        retail = True
        hotel = True
        wholesale = True
        distribution = True
        general = True
        flt = "today"
        total = 0
        no = 0
        sr = None
        sale = Sale.objects.filter(t_type='payment', date__date__gte=sd, date__date__lte=ed).order_by('-date')
    total = sale.aggregate(Sum('received'))['received__sum']
    no = sale.count()
    users = User.objects.values_list('username', flat=True)
    context = {'sale': sale, 'sd': sd, 'ed': ed, 'flt': flt, 'total': total, 'no': no, 'sr': sr,
                   'all':all,'retail':retail,'hotel':hotel,'wholesale':wholesale,'distribution':distribution,'general':general, 'users':users,'group':group}
    return render(request, 'adm/adm_payment_report.html', context)


@login_required(login_url='login')
def party_statement(request):
    try:
        # sd = datetime.datetime(now.year, now.month, 1).date()
        # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(seconds=1)
        # ed = ed.date()
        # active_process_balance(party, sd, ed)

        partys = Party.objects.all()
        data = {'partys': partys, 'party': {'party_name': '---Select Party---'}}
        # sd = timezone.now().date()
        # ed = timezone.now().date() + datetime.timedelta(days=1)

        now = timezone.now()
        sd = datetime.datetime(now.year, now.month, 1).date()

        print("=========================================")
        dt = datetime.datetime(now.year, now.month , 1)
        ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)- datetime.timedelta(seconds=1)
        print(ed)

        # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(seconds=1)
        ed = ed.date()
        if request.method == 'POST':
            party = Party.objects.get(party_name=request.POST['s_party'])
            active_process_balance(party, sd, ed)
            # sale = Sale.objects.filter(party_name=Party.objects.get(party_name=request.POST['s_party']),
            #                            date__range=[sd, ed]).order_by('date')
            # data = {'filter': 'This Month', 'partys': partys, 'party': party, 'sale': sale, 'sd': sd,
            #         'ed': ed - datetime.timedelta(days=1)}
        elif request.GET.get('data') is not None:
            party = Party.objects.get(id=request.GET.get('data'))
            active_process_balance(party, sd, ed)
        sale = Sale.objects.filter(Q(party_name=Party.objects.get(party_name=party.party_name)),
                                   Q(date__date__range=[sd, ed])).order_by('date')
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
        data = {'filter': 'This Month', 'partys': partys, 'party': party, 'sale': sale, 'sd': sd,
                'ed': ed - datetime.timedelta(days=1), 'total': total, 'no': no}
        if request.user.groups.filter(name="staff").exists():
            return render(request, 'staff/party_statement.html', data)
        return render(request, 'adm/party_statement.html', data)
    # except ObjectDoesNotExist:
    #     return HttpResponse('No data to found Error Code: party_statement')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    


@login_required(login_url='login')
def party_statement_date(request):
    try:
        partys = Party.objects.all()
        party = Party.objects.get(party_name=request.POST['party'])
        path = '?data=' + str(party.id)
        if request.POST.get('sd') == '' or request.POST.get('ed') == '':
            return redirect(reverse('party_statement') + path)

        sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
        ed = datetime.datetime.strptime(request.POST['ed'], "%Y-%m-%d").date() + datetime.timedelta(days=1)
        active_process_balance(party, sd, ed)
        sale = Sale.objects.filter(Q(party_name=Party.objects.get(party_name=party.party_name)),
                                Q(date__date__range=[sd, ed])).order_by('date')
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
        data = {'filter': False, 'partys': partys, 'party': party, 'sale': sale, 'sd': sd,
                'ed': ed - datetime.timedelta(days=1), 'total': total, 'no': no}
        if request.user.groups.filter(name="staff").exists():
            return render(request, 'staff/party_statement.html', data)
        return render(request, 'adm/party_statement.html', data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement_date',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def party_statement_filter(request):
    try:
        # partys = Party.objects.all()
        party = Party.objects.get(party_name=request.POST['party'])
        # path = '?data=' + str(party.id)
        flt = request.POST['filter']
        sd = None
        ed = None
        now = timezone.now()
        if flt == 'today':
            sd = timezone.now().date()
            ed = timezone.now().date() + datetime.timedelta(days=1)
            active_process_balance(party, sd, ed)
        elif flt == 'yesterday':
            sd = timezone.now().date() - datetime.timedelta(days=1)
            ed = timezone.now().date()
            active_process_balance(party, sd, ed)
        elif flt == 'This Month':
            sd = datetime.datetime(now.year, now.month, 1).date()
            # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(seconds=1)
            # ed = ed.date()
            dt = datetime.datetime(now.year, now.month, 1)
            ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
        
            print('ed :',ed)
            active_process_balance(party, sd, ed)
        elif flt == 'Prev Month':
            # sd = datetime.datetime(now.year, now.month - 1, 1).date()
            sd = (datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)).date()
            ed = datetime.datetime(now.year, now.month, 2) - datetime.timedelta(seconds=1)
            ed = ed.date()
            active_process_balance(party, sd, ed)
        elif flt == 'This Year':
            sd = datetime.datetime(now.year, 1, 1)
            ed = datetime.datetime.today() + datetime.timedelta(days=1)
            active_process_balance(party, sd, ed)

        sale = Sale.objects.filter(Q(party_name=Party.objects.get(party_name=party.party_name)),
                                Q(date__date__range=[sd, ed])).order_by('date')
        if flt == 'all':
            ed = timezone.now().date() + datetime.timedelta(days=1)
            sd = Sale.objects.filter(party_name=Party.objects.get(party_name=party.party_name)).first().date
            sd = sd - datetime.timedelta(days=1)
            active_process_balance(party, sd, ed)
            sale = Sale.objects.filter(party_name=Party.objects.get(party_name=party.party_name)).order_by('date')
        total = 0
        no = 0
        for i in sale:
            total += i.total
            no += 1
        data = {'filter': flt, 'party': party, 'sale': sale, 'sd': sd,
                'ed': ed - datetime.timedelta(days=1), 'total': total, 'no': no}
        if request.user.groups.filter(name="staff").exists():
            return render(request, 'staff/party_statement.html', data)
        return render(request, 'adm/party_statement.html', data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement_filter',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_product(request):
    try:
        if request.method == 'POST':
            prof = Products()
            prof.pname = request.POST['name']
            prof.size = request.POST['size']
            prof.HSN = request.POST['hsn']
            prof.barcode = request.POST['barcode']
            prof.mrp = request.POST['mrp']
            prof.r_price = request.POST['r_price']
            prof.w_price = request.POST['w_price']
            prof.h_price = request.POST['h_price']
            prof.d_price = request.POST['d_price']
            prof.save()
            messages.success(request, 'New product added for ' + prof.pname)

            Log.objects.create(user=request.user, process='Add Product', reference=prof.pname)  # Log_added
            return redirect('view_products')
        return render(request, 'adm/add_product.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_product',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def party_report(request):
    party = Party.objects.all()
    route = 'All'
    search = None
    all =True
    retail = True
    hotel = True
    wholesale = True
    distribution = True
    general = True
    fasal = True
    other = True
    allg = True
    if request.method == 'POST':
        search = request.POST['search']
        # route = request.POST['route']
        retail = request.POST.get('retail')
        hotel = request.POST.get('hotel')
        wholesale = request.POST.get('wholesale')
        distribution = request.POST.get('distribution')
        general = request.POST.get('general')
        fasal = request.POST.get('fasal')
        other = request.POST.get('other')
        print("other===>",other)
        # if route == 'All':
        #     party = Party.objects.filter(party_name__icontains=search) | Party.objects.filter(
        #         address__icontains=search)
        # else:
        #     party = Party.objects.filter(party_name__icontains=search, route=route) | Party.objects.filter(
        #         address__icontains=search, route=route)
        p_types = []
        
        if retail:
            p_types.append('Retail')
            retail = True
        if hotel:
            p_types.append('Hotel')
            hotel = True            
        if wholesale:
            p_types.append('Wholesale')
            wholesale = True
        if distribution:
            distribution = True
            p_types.append('Distribution')
        if general:
            general = True
            p_types.append('General')
        party_group = []
        if fasal:
            fasal = True
            print("enter")
            party_group.append('fasal')
        if other:
            party_group.append('other')
            other = True
        if retail and hotel and wholesale and distribution and general:
            all = True
        else:
            all = False
        if fasal and other:
            allg = True
        else:
            allg = False
        print("party_group==>",party_group)
        party = Party.objects.filter(type__in=p_types,party_group__in=party_group)
        party = party.filter(party_name__icontains=search) | party.filter(address__icontains=search)
        
    total_credit = party.aggregate(total_credit=Sum('balance'))['total_credit'] or 0
    no = party.count()
        
    # party pagination
    p = Paginator(party, 50)
    page_number = request.GET.get('page')
    try:
        party = p.get_page(page_number)
    except PageNotAnInteger:
        party = p.page(1)
    except EmptyPage:
        party = p.page(p.num_pages)               
    #end pagination
    
    return render(request, 'adm/adm_party_report_new.html', {'party': party, 'route': route, 'search': search,'all':all,'retail':retail,'hotel':hotel,'wholesale':wholesale,'distribution':distribution,'general':general,'fasal':fasal,'other':other,'allg':allg,'total_credit':total_credit,'no':no})
    # return render(request, 'adm/adm_party_report.html', {'party': party, 'route': route, 'search': search})


@login_required(login_url='login')
def party_view(request):
    try:
        today = datetime.datetime.today().date()
        if request.method == 'POST':
            party = Party.objects.get(id=request.POST['id'])
            if request.FILES.get('image') is None:
                image=party.image
            else:
                image = request.FILES['image']
            if request.POST.get('party_type'):
                    party_type = request.POST['party_type']
            else:
                party_type = "seller"
            party_group = request.POST.get('party_group')
            if not party_group:
                party_group = 'fasal'
            party.party_name = request.POST['name']
            party.address = request.POST['add']
            party.phone = request.POST['phone']
            party.whatsapp = request.POST['whatsapp']
            party.email = request.POST['email']
            party.GSTIN = request.POST['gst']
            party.type = request.POST['type']
            party.route = request.POST['rt']
            party.owner = request.POST['owner']
            party.category = request.POST['cat']
            party.party_group = party_group
            party.party_type = party_type
            party.image = image
            party.save()
            return redirect(reverse('party_view') + '?data=' + request.POST['id'])
        id = request.GET['data']
        party = Party.objects.get(id=id)
        sale = Sale.objects.filter(party_name=Party.objects.get(party_name=party.party_name)).order_by('-date')
        # sale pagination
        p = Paginator(sale, 50)
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)               
        #end pagination

        # WhatsApp
        if party.whatsapp:
            whats_app = party.whatsapp
        else:
            whats_app = party.phone
            
        data = {'party': party, 'sale': page_obj,'whats_app':whats_app}
        if request.user.groups.filter(name="admin").exists():
            return render(request, 'adm/party_view.html', data)
        else:
            if party.type == 'General' or party.type == 'Distribution':
                party = None
                Log.objects.create(
                    user=request.user,
                    type='Warning',
                    process='party_view',
                    reference = 'Permission Denied'
                )
                return render(request, 'error.html', {'code':'403', 'error':'Permission Denied!'})
            data = {'party': party, 'sale': page_obj, 'today': today,'whats_app':whats_app}
            return render(request, 'staff/party_view.html', data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement_date',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def home(request):
    # try:
        # Sunday
        today = datetime.date.today()
        is_sunday = (today.weekday() == 6)
        # End sunday

        sett = Settings.objects.get(user=request.user)
        profile = Profile.objects.all()
        count_msg = Messages.objects.all().count()
        notn = Alert.objects.filter(user=request.user)
        sr = None
        credit = False
        cr = 0
        if request.GET.get('credit') is not None:
            credit = request.GET['credit']
        party_ob = {'party_name': '-----Select a Party-----'}
        route = 'All'
        count = Sale.objects.filter(t_type='order').count()
        total = 0
        now = timezone.now()
        # psd = datetime.datetime(now.year, now.month - 1, 1).date()
        ped = datetime.datetime(now.year, now.month, 2) - datetime.timedelta(days=2)
        ped = ped.date()
        sd = datetime.datetime(now.year, now.month, 1).date()
        # ed = datetime.datetime(now.year, now.month + 1, 2) - datetime.timedelta(days=2)
        # ed = ed.date()
        dt = datetime.datetime(now.year, now.month, 1)
        ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
        psd = dt - relativedelta(months=1)
        

        if request.user.groups.filter(name="admin").exists():
            party = Party.objects.all().order_by('-updated')
            month_sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed])
            month_tot = month_sale.aggregate(total=Sum('total'))['total'] or 0
            # for i in month_sale:
            #     month_tot += i.total
            #     total = total + i.amount
            prev_sale = Sale.objects.filter(t_type='sale', date__date__range=[psd, ped])
            prev_tot = prev_sale.aggregate(total=Sum('total'))['total'] or 0
            # for i in prev_sale:
            #     prev_tot += i.total

            if credit == '1':
                party = Party.objects.all().order_by('-balance')
            sale = Sale.objects.filter(date__date__gte=timezone.now().date())
            for i in sale:
                total += i.received
            tot_sale = 0
            sale = Sale.objects.filter(t_type='sale', date__date__gte=timezone.now().date())
            total = sale.aggregate(total=Sum('total'))['total'] or 0
            # for i in sale:
            #     tot_sale += i.total
            exp = 0
            ex = Expense.objects.filter(date__date__gt=sd, date__date__lt=ed)
            exp = ex.aggregate(total=Sum('amount'))['total'] or 0
            # for i in ex:
            #     exp += i.amount

            if request.method == 'POST':
                sr = request.POST['search']
                route = request.POST['route']
                if route == 'All':
                    party = Party.objects.filter(party_name__icontains=sr) | Party.objects.filter(
                        address__icontains=sr).order_by('-updated')
                else:
                    party = Party.objects.filter(party_name__icontains=sr, route=route) | Party.objects.filter(
                        address__icontains=sr, route=route).order_by('-updated')
            # party pagination
            p = Paginator(party, 50)
            page_number = request.GET.get('page')
            try:
                page_obj = p.get_page(page_number)
            except PageNotAnInteger:
                page_obj = p.page(1)
            except EmptyPage:
                page_obj = p.page(p.num_pages)               
            #end pagination
            
            p = Party.objects.all()
            for i in p:
                cr += i.balance
            if prev_tot is 0:
                sale_increment = 0
            else:
                sale_increment = ((month_tot - prev_tot) / prev_tot) * 100
            data = {'route': route, 'count': count, 'total': total, 'sr': sr, 'cr': cr, 'month_tot': month_tot,
                    'prev_tot': prev_tot, 'sale_increment':round(sale_increment,2),
                    'this_month': sd, 'month_end': ed, 'expense': exp, 'tot_sale': tot_sale}

            return render(request, 'adm/home.html',
                        {'data': data, 'party': party,'party_pg':page_obj, 'party_ob': party_ob, 'sett': sett, 'profile': profile,
                        'count_msg': count_msg, 'notn':notn,'is_sunday':is_sunday})
        else:
            party = Party.objects.exclude(Q(type='Distribution') | Q(type='General')).order_by('-updated')

            month_sale = Sale.objects.filter(Q(t_type='sale'), Q(date__date__range=[sd, ed]),
                                            Q(party_type='Retail') | Q(party_type='Wholesale') | Q(party_type='Hotel'))
            month_tot = month_sale.aggregate(total=Sum('total'))['total'] or 0
            # for i in month_sale:
            #     month_tot += i.total
            prev_sale = Sale.objects.filter(Q(t_type='sale'), Q(date__date__range=[psd, ped]),
                                            Q(party_type='Retail') | Q(party_type='Wholesale') | Q(party_type='Hotel'))
            prev_tot = prev_sale.aggregate(total=Sum('total'))['total'] or 0
            # for i in prev_sale:
            #     prev_tot += i.total

            if credit == '1':
                party = party.order_by('-balance')

            if request.method == 'POST':
                sr = request.POST['search']
                route = request.POST['route']
                if route == 'All':
                    party = Party.objects.filter(Q(type='Retail') | Q(type='Wholesale') | Q(type='Hotel'),
                                                party_name__icontains=sr) | \
                            Party.objects.filter(Q(type='Retail') | Q(type='Wholesale') | Q(type='Hotel'),
                                                address__icontains=sr).order_by('-updated')
                else:
                    party = Party.objects.filter(Q(type='Retail') | Q(type='Wholesale') | Q(type='Hotel'),
                                                party_name__icontains=sr, route=route) | \
                            Party.objects.filter(Q(type='Retail') | Q(type='Wholesale') | Q(type='Hotel'),
                                                address__icontains=sr, route=route).order_by('-updated')
            # party pagination
            p = Paginator(party, 50)
            page_number = request.GET.get('page')
            try:
                page_obj = p.get_page(page_number)
            except PageNotAnInteger:
                page_obj = p.page(1)
            except EmptyPage:
                page_obj = p.page(p.num_pages)               
            #end pagination
            # sale = Sale.objects.filter(user=request.user, t_type='payment', date__date__gte=timezone.now().date())
            t_type = ['payment','sale']
            total = Sale.objects.filter(party_name__party_group='fasal',t_type__in=t_type, date__date__gte=timezone.now().date()).aggregate(received_sum=Sum('received'))['received_sum'] or 0
            
            # This month collection
            t_sd = datetime.datetime(now.year, now.month, 1).date()
            dt = datetime.datetime(now.year, now.month, 1)
            t_ed = (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
            p_sd = (datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)).date()
            p_ed = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(seconds=1)
            p_ed = p_ed.date()
            
            this_month = Sale.objects.filter(party_name__party_group='fasal', t_type__in=t_type, date__date__gte=t_sd,date__date__lte=t_ed).aggregate(received_sum=Sum('received'))['received_sum'] or 0
            prev_month_coll = Sale.objects.filter(party_name__party_group='fasal', t_type__in=t_type, date__date__gte=p_sd,date__date__lte=p_ed).aggregate(received_sum=Sum('received'))['received_sum'] or 0
            # print("this_month====>",this_month)
            # for i in sale:
            #     total += i.received
            p = Party.objects.filter(Q(type='Retail') | Q(type='Wholesale') | Q(type='Hotel')).order_by('-updated')
            for i in p:
                cr += i.balance
            exp = 0
            ex = Expense.objects.filter(user=request.user, date__date__gt=sd, date__date__lt=ed)
            for i in ex:
                exp += i.amount

            # order pending Count
            pt = Party.objects.exclude(Q(type='Distribution') | Q(type='General')).order_by('-updated')
            count = 0
            sl = Sale.objects.filter(t_type='order')
            for i in sl:
                for j in pt:
                    if str(i.party_name) == str(j.party_name):
                        count += 1
            # End Staff Count
            data = {'route': route, 'count': count, 'total': total, 'sr': sr, 'cr': cr, 'month_tot': month_tot,
                    'prev_tot': prev_tot,'this_month_coll':this_month,'prev_month_coll':prev_month_coll,
                    'this_month': sd, 'month_end': ed, 'expense': exp}
            prof = Profile.objects.get(user=request.user)
            return render(request, 'staff/home.html', {'prof':prof, 'data': data, 'party': party,'party_pg':page_obj, 'party_ob': party_ob,
                                                    'sett': sett, 'notn': notn,'is_sunday':is_sunday})
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
    #     Log.objects.create(
    #         user=request.user,
    #         type='Error',
    #         process='home',
    #         reference = err_descrb
    #     )
    #     return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

# OOOOOOOOOOOOOOOOOOOrder

@login_required(login_url='login')
def add_order(request):
    try:
        with transaction.atomic():
            if Prefix.objects.filter(used='order', active=True).exists():
                pr = Prefix.objects.get(used='order', active=True)
                prefix = pr.prefix
                last_id = pr.last_id
            else:
                prefix = 'OD'
                last_id = 0
                Prefix.objects.create(prefix=prefix, last_id=int(last_id), used='order', active=True)
            new_s_no = last_id + 1
            partys = Party.objects.all()
            product = Products.objects.filter(active=True).order_by('pname')
            dt = datetime.date.today() + datetime.timedelta(days=1)
            sl_itm = None
            party_ob = {'party_name': '-----Select a Party-----'}
            odr = 0
            cb = 0
            t_type = 0
            if request.method == 'POST':
                party = request.POST['s_party']
                party_ob = Party.objects.get(party_name=Party.objects.get(party_name=party))
                # if Sale.objects.filter(s_id=new_s_no).exists():
                #     od = Sale_item.objects.filter(s_id=Sale.objects.get(s_id=new_s_no))
                # else:
                #     od = None
            if request.GET.get('party') is not None:
                party = request.GET['party']
                party_ob = Party.objects.get(id=party)
            if request.GET.get('data') is not None:
                sale_id = request.GET.get('data')
                odr = Sale.objects.get(id=sale_id)
                new_s_no = odr.s_id
                prefix = odr.id_prefix
                party_ob = Party.objects.get(party_name=odr.party_name)
                dt = odr.date
                sl_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=odr.iid))
                cb = odr.total + party_ob.balance
                if odr.t_type == 'order':
                    t_type = 0
                elif odr.t_type == 'payment':
                    t_type = 2
            if request.user.groups.filter(name="admin").exists():
                return render(request, 'adm/add_order.html',
                            {'party': partys, 'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob,
                            'dt': dt, 'sale': sl_itm, 'odr': odr, 'cb': cb, 't_type': t_type})
            else:
                partys = Party.objects.exclude(Q(type='Distribution') | Q(type='General'))
                return render(request, 'staff/add_order.html',
                            {'party': partys, 'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob,
                            'dt': dt, 'sale': sl_itm, 'odr': odr, 'cb': cb, 't_type':t_type})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_order',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def add_order_item(request):
    try:
        with transaction.atomic():
            party_name = request.GET['party_name']
            pname = request.GET['pname']
            price = float(request.GET['price'])
            qty = request.GET['qty']
            fqty = request.GET['fqty']
            od_no = int(request.GET['od_no'])
            date = request.GET['date']
            prefix = request.GET['prefix']
            stock = 0  # error
            if fqty == '':
                fqty = 0
            else:
                fqty = float(fqty)
            if qty == '':
                qty = 0
            else:
                qty = float(qty)
            amount = float(price) * float(qty)
            tot = 0
            iid = prefix + str(od_no)
            # if Prefix.objects.filter(used='sale', active=True).exists():
            prfx = Prefix.objects.get(used='order', active=True)
            if Sale.objects.filter(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix)).exists():
                sl = Sale.objects.get(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix))
                if str(party_name) != str(sl.party_name):
                    # print('Invoice number already exists')
                    msg = 1
                    messages.info(request, 'Invoice number already exists')
                    data = {'msg': msg}
                    return JsonResponse(data)
            now = timezone.now()
            current_time = now.strftime("%H:%M:%S")
            dt_string = date + current_time
            fom = "%Y-%m-%d%H:%M:%S"
            print('dt_string =', dt_string)
            dt_object = datetime.datetime.strptime(dt_string, fom)
            if not Sale.objects.filter(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix)).exists():
                # print("ENTERED FirstItem to add IF")
                t_amount = amount * (95.2385 / 100)
                gst = t_amount * (2.5 / 100)
                par = Party.objects.get(party_name=party_name)
                Sale.objects.create(s_id=od_no, iid=iid, party_name=Party.objects.get(party_name=party_name),
                                    party_type=par.type,
                                    id_prefix=Prefix.objects.get(prefix=prefix), date=dt_object, total=amount,
                                    t_total=t_amount, received=0,
                                    t_type='order', balance=Party.objects.get(party_name=party_name).balance,
                                    user=User.objects.get(username=request.user.username))

                t_price = price * (95.2385 / 100)
                sitm = Sale_item.objects.create(iid=Sale.objects.get(iid=iid),
                                                party_name=Party.objects.get(party_name=party_name),
                                                p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)
                sal = Sale.objects.get(iid=iid)
                sal.q_total += qty
                sal.fq_total += fqty
                sal.save()
                tot = amount
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()
                # print("SAVEEEDDDDDDDD 1st")
                stock = 1  # 1st Item Added
                Log.objects.create(user=request.user, process='Add order', reference=iid + ' : ' + str(party_name) + ' :B=' + str(par.balance))  # Log_added
            elif Sale_item.objects.filter(iid=Sale.objects.get(iid=iid),
                                        p_name=Products.objects.get(pname=pname)).exists():
                # print("Alrady ind Product Replaced ELIF")
                sitm = Sale_item.objects.get(iid=Sale.objects.get(iid=iid),
                                            p_name=Products.objects.get(pname=pname))
                sl = Sale.objects.get(iid=iid)
                sl.total = (sl.total - sitm.amount) + amount
                sl.t_total = sl.total * (95.2385 / 100)
                # sl.g_total = sl.t_total * (2.5 / 100)
                sl.q_total = (sl.q_total - sitm.qty) + qty
                sl.fq_total = (sl.fq_total - sitm.fqty) + fqty
                tot = sl.total
                sl.save()
                sitm.pname = pname
                sitm.price = price
                sitm.qty = qty
                sitm.fqty = fqty
                sitm.amount = amount
                sitm.t_price = price * (95.2385 / 100)
                sitm.t_amount = amount * (95.2385 / 100)
                sitm.gst = sitm.t_amount * (2.5 / 100)
                sitm.save()
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()

                stock = 2  # Product Replaced
                # print("ALREDY ind Compleeted")
                Log.objects.create(user=request.user, process='Add order Replaced', reference=iid + ' : ' + party_name)  # Log_added
            else:
                # print("Added Another item ELSE")
                stock = 1
                sl = Sale.objects.get(iid=iid)
                sl.total = sl.total + amount
                sl.t_total = sl.total * (95.2385 / 100)
                # sl.g_total = sl.t_total * (2.5 / 100)
                sl.q_total += qty
                sl.fq_total += fqty
                sl.save()
                tot = sl.total

                t_price = price * (95.2385 / 100)
                t_amount = amount * (95.2385 / 100)
                gst = t_amount * (2.5 / 100)
                sitm = Sale_item.objects.create(iid=Sale.objects.get(iid=iid),
                                                party_name=Party.objects.get(party_name=party_name),
                                                p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)
                sitm.save()
                Log.objects.create(user=request.user, process='Add order another', reference=iid + ' : ' + party_name)  # Log_added
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()
            lt = Sale.objects.filter(party_name=Party.objects.get(party_name=party_name)).latest('date')
            pt = Party.objects.get(party_name=party_name)
            pt.updated = lt.date
            pt.save()
            data = {'id': sitm.id, 'pname': pname, 'qty': qty, 'amt': amount, 'tot': tot, 'stock': stock}
            return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_order_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def delete_order_item(request):
    try:
        with transaction.atomic():
            itm_id = request.GET['itm_id']
            sitm = Sale_item.objects.get(id=itm_id)
            sid = str(sitm.iid)
            sl = Sale.objects.get(iid=sid)
            sl.total = sl.total - sitm.amount
            sl.t_total = sl.total * (95.2385 / 100)
            # sl.g_total = sl.t_total * (2.5 / 100)
            sl.q_total -= sitm.qty
            sl.fq_total -= sitm.fqty
            tot = sl.total
            sl.save()
            sitm.delete()
            Log.objects.create(user=request.user, process='Delete order item', reference=sid + ' : ' + str(sl.party_name)+ ':' + str(sl.party_name.balance))  # Log_added
            if not Sale_item.objects.filter(iid=Sale.objects.get(iid=sid)).exists():
                pr = Sale.objects.get(iid=sid).party_name
                Sale.objects.get(iid=sid).delete()
                Log.objects.create(user=request.user, process='Delete order', reference=sid + ' : ' + str(sl.party_name)+ ':' + str(sl.party_name.balance))  # Log_added
                lt_id = Sale.objects.filter(party_name=Party.objects.get(party_name=pr)).latest('date')
                pt = Party.objects.get(party_name=pr)
                pt.updated = lt_id.date
                pt.save()
                prfx = Prefix.objects.get(used='order', active=True)
                max = Sale.objects.filter(id_prefix=sl.id_prefix).aggregate(Max('s_id')).get('s_id__max')
                prfx.last_id = max
                prfx.save()
            data = {'deleted': True, 'tot': tot}
            return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_order_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def deleteOrder(request):
    try:
        iid = request.GET['iid']
        sale = Sale.objects.get(iid=iid)
        pr = Sale.objects.get(iid=iid).party_name
        sale.delete()
        Log.objects.create(user=request.user, process='Delete order', reference=iid + ' : ' + str(pr) + '|B:'+ str(pr.balance))  # Log_added
        lt_id = Sale.objects.filter(party_name=Party.objects.get(party_name=pr)).latest('date')
        pt = Party.objects.get(party_name=pr)
        pt.updated = lt_id.date
        pt.save()
        prfx = Prefix.objects.get(used='order', active=True)
        max = Sale.objects.filter(id_prefix=sale.id_prefix).aggregate(Max('s_id')).get('s_id__max')
        if max is None:
            max = 0
        prfx.last_id = max
        prfx.save()
        data = 1
        if request.GET.get('id') is None:
            return redirect('view_orders')
    except ObjectDoesNotExist:
        data = 0
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='deleteOrder',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    
    return HttpResponse(data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def OrderToSale(request):
    try:
        with transaction.atomic():
            if request.method == 'POST':
                id = request.POST['id']
                s_date = request.POST['s_date']
                s_no = request.POST['s_no']
                prefix = request.POST['prefix']
                tot = request.POST['tot']
                received = request.POST['received']
                if received == '':
                    received = 0
                type = request.POST['type']
                sl = Sale.objects.get(id=id)
                last = Sale.objects.latest('date')
                sl.s_id = s_no
                sl.id_prefix = Prefix.objects.get(prefix=prefix)
                sl.iid = prefix + str(s_no)
                sl.date = s_date
                sl.t_type = 'sale'
                sl.received = float(received)
                sl.p_type = type
                party = Party.objects.get(party_name=sl.party_name)
                party.balance = sl.balance = (float(party.balance) + float(tot)) - float(received)
                sl.balance = party.balance
                sl.updated = last.date
                sl.save()
                party.save()
                prfx = Prefix.objects.get(used='sale', active=True)
                Log.objects.create(user=request.user, process='Order to Sale', reference=sl.iid + ' : ' + str(sl.party_name)+ ' |OB: ' + str(sl.party_name.balance))  # Log_added
                if int(s_no) > prfx.last_id:
                    prfx.last_id = s_no
                    prfx.save()
                # return redirect('view_orders')
                path = '?id=' + str(sl.id)
                return redirect(reverse('invoice_view') + path)
            pr = Prefix.objects.get(used='sale', active=True)
            s_prefix = pr.prefix
            last_id = Sale.objects.filter(id_prefix=Prefix.objects.get(prefix=s_prefix)).aggregate(Max('s_id')).get(
                's_id__max')
            # last_id = pr.last_id
            new_s_no = last_id + 1
            product = Products.objects.all()
            sale_id = request.GET.get('data')
            odr = Sale.objects.get(id=sale_id)
            party_ob = Party.objects.get(party_name=odr.party_name)
            s_date = datetime.date.today()
            dt = odr.date
            new_od_no = odr.s_id
            prefix = odr.id_prefix
            sl_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=odr.iid))
            cb = odr.total + party_ob.balance
            return render(request, 'adm/cToSale.html',
                        {'new_s_no': new_s_no, 's_prefix': s_prefix, 's_date': s_date, 'product': product, 'od_no': new_od_no,
                        'prefix': prefix, 'party_ob': party_ob, 'dt': dt, 'sale': sl_itm, 'odr': odr, 'cb': cb})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='OrderToSale',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

# OOOOOOOOOOOOOOOOOOO

# SSSSSSSSSSSSSSSSale
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_sale(request):
    try:
        with transaction.atomic():
            if Prefix.objects.filter(used='sale', active=True).exists():
                pr = Prefix.objects.get(used='sale', active=True)
                prefix = pr.prefix
                last_id = Sale.objects.filter(id_prefix=Prefix.objects.get(prefix=prefix)).aggregate(Max('s_id')).get(
                    's_id__max')
                if last_id is None:
                    last_id = 0
            else:
                prefix = 'JC'
                last_id = 0
                Prefix.objects.create(prefix=prefix, last_id=int(last_id), used='sale', active=True)
            new_s_no = last_id + 1
            partys = Party.objects.all()
            product = Products.objects.filter(active=True).order_by('pname')
            dt = datetime.date.today()
            sl_itm = None
            party_ob = {'party_name': '-----Select a Party-----'}
            sale = None
            ob = 0
            cb = 0
            if request.method == 'POST':
                party = request.POST['s_party']
                party_ob = Party.objects.get(party_name=Party.objects.get(party_name=party))
                cb = ob = party_ob.balance
            elif request.GET.get('party') is not None:
                party = request.GET['party']
                party_ob = Party.objects.get(id=party)
                cb = ob = party_ob.balance
            if request.GET.get('data') is not None:
                sale_id = request.GET.get('data')
                sale = Sale.objects.get(id=sale_id)
                new_s_no = sale.s_id
                prefix = sale.id_prefix
                dt = sale.date
                party_ob = Party.objects.get(party_name=sale.party_name)
                cb = party_ob.balance
                ob = cb - sale.total
                sl_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid))

            return render(request, 'adm/add_sale.html',
                        {'party': partys, 'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob,
                        'dt': dt, 'sale': sl_itm, 'odr': sale, 'ob': ob, 'cb': cb})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_sale',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

# SALE RETURN
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def sale_return(request):
    try:
        with transaction.atomic():
            if Prefix.objects.filter(used='return', active=True).exists():
                pr = Prefix.objects.get(used='return', active=True)
                prefix = pr.prefix
                last_id = Sale.objects.filter(id_prefix=Prefix.objects.get(prefix=prefix)).aggregate(Max('s_id')).get(
                    's_id__max')
                if last_id is None:
                    last_id = 0
            else:
                prefix = 'RT'
                last_id = 0
                Prefix.objects.create(prefix=prefix, last_id=int(last_id), used='return', active=True)
            new_s_no = last_id + 1

            product = Products.objects.filter(active=True).order_by('pname')
            today = datetime.date.today()
            sl_itm = None
            party_ob = {'party_name': '-----Select a Party-----'}
            sale = None
            ob = 0
            cb = 0
            count = 0
            i_no = None
            if request.GET.get('data') is not None:
                sale_id = request.GET.get('data')
                sale = Sale.objects.get(id=sale_id)
                dt = sale.date
                party_ob = Party.objects.get(party_name=sale.party_name)
                cb = party_ob.balance
                ob = cb - sale.total
                sl_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid))
                count = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid)).count()

            if request.method == 'POST':
                iid = str(prefix) + str(new_s_no)
                party = Party.objects.get(party_name=request.POST['party'])
                if request.POST['paid'] == '':
                    paid = 0
                else:
                    paid = float(request.POST['paid'])
                total = float(request.POST['total'])
                t_total = total * (95.2385 / 100)
                balance = party.balance - (total - paid)
                i_iid = request.POST['i_no']

                party.balance = balance
                party.save()
                Sale.objects.create(s_id=new_s_no,id_prefix=Prefix.objects.get(prefix=prefix), iid=iid, party_name=party,
                                    party_type=party.type, date=request.POST['date'], t_type='return', total=total * -1,
                                    t_total=t_total * -1, received=paid * -1, p_type=request.POST['p_type'], balance=balance,
                                    user=request.user, ir_date=request.POST['i_date'], ir_iid=i_iid)

                # Return.objects.create(i_date=request.POST['i_date'], i_iid=i_iid, iid=Sale.objects.get(iid=iid))

                n = Sale_item.objects.filter(iid=Sale.objects.get(iid=i_iid)).count()
                t_qty = 0
                t_fqty = 0
                for i in range(1, n+1):
                    if not (request.POST.get('qty' + str(i)) == '' or request.POST.get('price' + str(i)) == ''):
                        pname = request.POST.get('name'+str(i))
                        print('entered',pname)
                        qty = float(request.POST.get('qty'+str(i)))
                        if request.POST.get('fqty' + str(i)) == '':
                            fqty = 0
                        else:
                            fqty = float(request.POST.get('fqty' + str(i)))
                        t_qty += qty
                        t_fqty += fqty
                        price = request.POST.get('price'+str(i))
                        amount = float(price) * float(qty)
                        t_price = float(price) * (95.2385 / 100)
                        t_amount = amount * (95.2385 / 100)
                        gst = t_amount * (2.5 / 100)

                        if amount != 0:
                            Sale_item.objects.create(iid=Sale.objects.get(iid=iid), party_name=party,
                                                    p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                            gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)
                    else:
                        print('else worked :', request.POST.get('name'+str(i)))
                sl = Sale.objects.get(iid=iid)
                sl.q_total = t_qty
                sl.fq_total = t_fqty
                sl.save()
                path = '?data=' + str(party.id)

                Log.objects.create(user=request.user, process='Add Sale Return', reference=iid + ' : ' + str(party) + ' |B:' + str(sl.party_name.balance))  # Log_added
                return redirect(reverse('party_view') + path)

            return render(request, 'adm/sale_return.html',
                        {'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob,
                        'dt': dt, 'sale': sl_itm, 'odr': sale, 'ob': ob, 'cb': cb, 'today': today, 'count': count, 'i_no': i_no})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='sale_return',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def edit_return(request):
    try:
        with transaction.atomic():
            if request.method == 'POST':
                iid = request.POST['iid']
                party = Party.objects.get(party_name=request.POST['party'])
                sale = Sale.objects.get(iid=iid)
                paid = float(request.POST['paid'])
                total = float(request.POST['total'])
                t_total = total * (95.2385 / 100)
                party.balance = party.balance + (-sale.total - -sale.received)
                party.balance = party.balance - (total - paid)
                party.save()
                sale.date = request.POST['date']
                sale.total = total * -1
                sale.t_total = t_total * -1
                sale.received = paid * -1
                sale.p_type = request.POST['p_type']
                sale.balance = party.balance
                sale.save()
                n = int(request.POST['count'])
                Sale_item.objects.filter(iid=sale).delete()
                t_qty = 0
                t_fqty = 0
                for i in range(1, n+1):
                    if not (request.POST.get('qty' + str(i)) == '' or request.POST.get('price' + str(i)) == ''):
                        pname = request.POST.get('name' + str(i))
                        qty = float(request.POST.get('qty' + str(i)))
                        if request.POST.get('fqty' + str(i)) == '':
                            fqty = 0
                        else:
                            fqty = float(request.POST.get('fqty' + str(i)))
                        t_qty += qty
                        t_fqty += fqty
                        price = request.POST.get('price' + str(i))
                        amount = float(price) * float(qty)
                        t_price = float(price) * (95.2385 / 100)
                        t_amount = amount * (95.2385 / 100)
                        gst = t_amount * (2.5 / 100)

                        if amount != 0:
                            Sale_item.objects.create(iid=sale, party_name=party,
                                                    p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                    gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)

                path = '?data=' + str(party.id)
                return redirect(reverse('party_view') + path)

            sale_id = request.GET.get('data')
            sale = Sale.objects.get(id=sale_id)
            product = Products.objects.filter(active=True).order_by('pname')
            new_s_no = sale.s_id
            prefix = sale.id_prefix
            party_ob = Party.objects.get(party_name=sale.party_name)
            # rt = Return.objects.get(iid=sale)
            dt = sale.ir_date
            sl_itm = Sale_item.objects.filter(iid=sale)
            count = Sale_item.objects.filter(iid=sale).count()
            cb = party_ob.balance
            ob = cb - sale.total
            today = sale.date
            i_no = sale.ir_iid
            Log.objects.create(user=request.user, process='Add Sale Return', reference=sale.iid + ' : ' + str(sale.party_name) + ' |B:' + str(sale.party_name.balance))  # Log_added
            return render(request, 'adm/sale_return.html',
                        {'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob,
                        'dt': dt, 'sale': sl_itm, 'odr': sale, 'ob': ob, 'cb': cb, 'today':today, 'count':count, 'i_no':i_no})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='edit_return',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    

@login_required(login_url='login')
def update_sale(request):
    try:
        with transaction.atomic():
            t_type = 1
            if request.method == 'POST':
                iid = request.POST['iid']
                dt = request.POST['date']
                prefix = request.POST['prefix']
                od_no = request.POST['inv_no']
                report = request.POST['report']
                rc = request.POST['rc']
                if rc == '':
                    rc = 0
                p_type = request.POST['p_type']
                n_iid = prefix + str(od_no)
                sale = Sale.objects.get(iid=iid)
                if sale.t_type == 'order':
                    t_type = 0
                elif sale.t_type == 'payment':
                    t_type = 2
                    if Profile.objects.filter(user=sale.user).exists():
                        pr = Profile.objects.get(user=sale.user)
                        if sale.p_type == 'Cash':
                            if p_type == 'Cash':
                                pr.balance = (pr.balance - sale.received) + float(rc)
                                pr.save()
                            else:
                                pr.balance = pr.balance - sale.received
                                pr.save()
                        elif p_type == 'Cash':
                            pr.balance += float(rc)
                            pr.save()
                party = Party.objects.get(party_name=sale.party_name)
                party.balance = (party.balance + sale.received) - float(rc)
                sale.iid = n_iid
                now = timezone.now()
                current_time = now.strftime("%H:%M:%S")
                dt_string = dt + current_time
                fom = "%Y-%m-%d%H:%M:%S"
                dt_object = datetime.datetime.strptime(dt_string, fom)
                sale.date = dt_object
                sale.id_prefix = Prefix.objects.get(prefix=prefix)
                sale.s_id = od_no
                sale.received = rc
                sale.p_type = p_type
                sale.balance = party.balance
                sale.report = report
                sale.save()
                lt = Sale.objects.filter(party_name=Party.objects.get(party_name=sale.party_name)).latest('date')
                party.updated = lt.date
                party.save()
                Log.objects.create(user=request.user, process='Update Sale', reference=n_iid + ' : ' + str(sale.party_name) + ' |B: ' + str(sale.party_name.balance))  # Log_added
                path = '?data=' + str(party.id)
                return redirect(reverse('party_view') + path)
            sale_id = request.GET.get('data')
            sale = Sale.objects.get(id=sale_id)
            dte = sale.date.date()
            if sale.t_type == 'order':
                t_type = 0
            elif sale.t_type == 'payment':
                t_type = 2

            product = Products.objects.filter(active=True).order_by('pname')
            new_s_no = sale.s_id
            prefix = sale.id_prefix
            dt = sale.date
            party_ob = Party.objects.get(party_name=sale.party_name)
            # cb = sale.balance + sale.received
            # ob = cb - sale.total
            sl_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid))
            if request.user.groups.filter(name="admin").exists():
                return render(request, 'adm/update_sale.html',
                            {'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob, 'dt': dt,
                            'sale': sl_itm, 'odr': sale, 't_type': t_type})
            else:
                today = datetime.datetime.today().date()
                if dte == today and sale.t_type == 'payment' or sale.t_type == 'order':
                    return render(request, 'staff/update_order.html',
                                {'product': product, 'od_no': new_s_no, 'prefix': prefix, 'party_ob': party_ob, 'dt': dt,
                                'sale': sl_itm, 'odr': sale, 't_type': t_type})
                else:
                    Log.objects.create(
                        user=request.user,
                        type='Warning',
                        process='update_sale',
                        reference = 'Permission Denied' + '|' + str(sale.iid) + '|' + str(dte) + '|' + str(sale.t_type)
                    )
                    return render(request, 'error.html', {'code':'403', 'error':'Permission Denied!'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement_date',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
    


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_sale_item(request):
    try:
        with transaction.atomic():
            party_name = request.GET['party_name']
            pname = request.GET['pname']
            price = float(request.GET['price'])
            qty = request.GET['qty']
            fqty = request.GET['fqty']
            od_no = int(request.GET['od_no'])
            dt = request.GET['date']
            prefix = request.GET['prefix']
            rc = request.GET['rc']
            stock = 0  # error
            if fqty == '':
                fqty = 0
            else:
                fqty = float(fqty)
            if qty == '':
                qty = 0
            else:
                qty = float(qty)
            amount = float(price) * float(qty)
            tot = 0
            msg = 0
            iid = prefix + str(od_no)
            now = timezone.now().time()
            current_time = now.strftime("%H:%M:%S")
            dt_string = dt + current_time
            fom = "%Y-%m-%d%H:%M:%S"
            dt_object = datetime.datetime.strptime(dt_string, fom)
            td = timezone.now()
            prfx = Prefix.objects.get(used='sale', active=True)
            # multiple
            if Sale.objects.filter(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix)).exists():
                sl = Sale.objects.get(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix))
                if str(party_name) != str(sl.party_name):
                    msg = 1
                    messages.info(request, 'Invoice number already exists')
                    data = {'msg': msg}
                    return JsonResponse(data)
            if not Sale.objects.filter(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prefix)).exists():
                t_amount = amount * (95.2385 / 100)
                gst = t_amount * (2.5 / 100)
                t_price = price * (95.2385 / 100)
                par = Party.objects.get(party_name=party_name)
                Sale.objects.create(s_id=od_no, iid=iid, party_name=Party.objects.get(party_name=party_name),
                                    party_type=par.type,
                                    id_prefix=Prefix.objects.get(prefix=prefix), date=dt_object, total=amount,
                                    t_total=t_amount,
                                    received=0, t_type='sale', balance=par.balance,
                                    user=User.objects.get(username=request.user.username))
                sitm = Sale_item.objects.create(iid=Sale.objects.get(iid=iid),
                                                party_name=Party.objects.get(party_name=party_name),
                                                p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)
                sal = Sale.objects.get(iid=iid)
                sal.q_total += qty
                sal.fq_total += fqty
                sal.save()

                par.balance = par.balance + amount
                par.save()
                tot = amount
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()
                stock = 1  # 1st Item Added
                Log.objects.create(user=request.user, process='Add Sale', reference=iid + ' : ' + party_name+ ' |B: ' + str(par.balance))  # Log_added
            elif Sale_item.objects.filter(iid=Sale.objects.get(iid=iid), p_name=Products.objects.get(pname=pname)).exists():
                # print("Alrady ind Product Replaced ELIF")
                sitm = Sale_item.objects.get(iid=Sale.objects.get(iid=iid), p_name=Products.objects.get(pname=pname))
                sl = Sale.objects.get(iid=iid)
                sl.total = (sl.total - sitm.amount) + amount
                sl.t_total = sl.total * (95.2385 / 100)
                # sl.g_total = sl.t_total * (2.5 / 100)
                sl.q_total = (sl.q_total - sitm.qty) + qty
                sl.fq_total = (sl.fq_total - sitm.fqty) + fqty
                tot = sl.total
                par = Party.objects.get(party_name=party_name)
                par.balance = (par.balance - sitm.amount) + amount
                par.save()
                sl.save()
                # ss_id = sitm.id
                # sitm.delete()
                sitm.pname = pname
                sitm.price = price
                sitm.qty = qty
                sitm.fqty = fqty
                sitm.amount = amount
                sitm.t_price = price * (95.2385 / 100)
                sitm.t_amount = amount * (95.2385 / 100)
                sitm.gst = sitm.t_amount * (2.5 / 100)
                sitm.save()
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()

                '''
                sitm = Sale_item(s_id=Sale.objects.get(s_id=od_no), party_name=Party.objects.get(party_name=party_name),
                                p_name=Products.objects.get(pname=pname),
                                price=price, qty=qty, fqty=fqty, amount=amount)
                '''
                stock = 2  # Product Replaced
                Log.objects.create(user=request.user, process='Add Sale replaced', reference=iid + ' : ' + party_name)  # Log_added
                # print("ALREDY ind Compleeted")
            else:
                # print("Added Another item ELSE")
                stock = 1
                sl = Sale.objects.get(iid=iid)
                sl.total = sl.total + amount
                sl.t_total = sl.total * (95.2385 / 100)
                # sl.g_total = sl.t_total * (2.5 / 100)
                sl.q_total += qty
                sl.fq_total += fqty
                par = Party.objects.get(party_name=party_name)
                par.balance = par.balance + amount
                
                tot = sl.total

                t_price = price * (95.2385 / 100)
                t_amount = amount * (95.2385 / 100)
                gst = t_amount * (2.5 / 100)
                sitm = Sale_item.objects.create(iid=Sale.objects.get(iid=iid),
                                                party_name=Party.objects.get(party_name=party_name),
                                                p_name=Products.objects.get(pname=pname), price=price, t_price=t_price,
                                                gst=gst, qty=qty, fqty=fqty, amount=amount, t_amount=t_amount)
                sitm.save()
                par.save()
                sl.save()
                Log.objects.create(user=request.user, process='Add Sale another', reference=iid + ' : ' + party_name)  # Log_added
                if od_no > prfx.last_id:
                    prfx.last_id = od_no
                    prfx.save()

            lt = Sale.objects.filter(party_name=Party.objects.get(party_name=party_name)).latest('date')
            pt = Party.objects.get(party_name=party_name)
            pt.updated = lt.date
            pt.save()
            data = {'id': sitm.id, 'pname': pname, 'qty': qty, 'amt': amount, 'tot': tot, 'stock': stock}
            return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_sale_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})

@login_required(login_url='login')
def edit_sale_item(request):
    try:
        item_id = request.GET['tr_id']
        si = Sale_item.objects.get(id=item_id)
        itm = str(si.p_name)
        product = Products.objects.get(pname=si.p_name)
        party_ob = Party.objects.get(party_name=si.party_name)
        if party_ob.type == 'Retail':
            f_price = product.r_price
        elif party_ob.type == 'Hotel':
            f_price = product.h_price
        elif party_ob.type == 'Distribution':
            f_price = product.d_price
        elif party_ob.type == 'Wholesale':
            f_price = product.w_price
        else:
            f_price = 'Update party type First!'
        data = {'id': item_id, 'itm': itm, 'price': si.price, 'qty': si.qty, 'fqty': si.fqty, 'amt': si.amount,'f_price':f_price}
        return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='edit_sale_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_sale_item(request):
    try:
        with transaction.atomic():
            itm_id = request.GET['itm_id']
            sitm = Sale_item.objects.get(id=itm_id)
            sid = str(sitm.iid)
            sl = Sale.objects.get(iid=sid)
            sl.total = sl.total - sitm.amount
            sl.t_total = sl.total * (95.2385 / 100)
            # sl.g_total = sl.t_total * (2.5 / 100)
            sl.q_total -= sitm.qty
            sl.fq_total -= sitm.fqty
            tot = sl.total
            par = Party.objects.get(party_name=sitm.party_name)
            par.balance = par.balance - sitm.amount
            par.save()
            sl.save()
            sitm.delete()
            Log.objects.create(user=request.user, process='Delete Sale item', reference=sid + ' : ' + str(sl.party_name)+ ' |B: ' + str(sl.party_name.balance))  # Log_added
            if not Sale_item.objects.filter(iid=Sale.objects.get(iid=sl.iid)).exists():
                pn = Sale.objects.get(iid=sid).party_name
                lt = Sale.objects.filter(party_name=Party.objects.get(party_name=pn)).latest('date')
                Sale.objects.get(iid=sid).delete()
                prfx = Prefix.objects.get(used='sale', active=True)
                max = Sale.objects.filter(id_prefix=sl.id_prefix).aggregate(Max('s_id')).get('s_id__max')
                prfx.last_id = max
                prfx.save()
                pt = Party.objects.get(party_name=pn)
                pt.updated = lt.date
                pt.save()
                Log.objects.create(user=request.user, process='Delete Sale', reference=sid + ' : ' + pn+ ' |B: ' + str(pt.balance))  # Log_added
            data = {'deleted': True, 'tot': tot}
            return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_sale_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_sale_update_item(request):
    try:
        with transaction.atomic():
            itm_id = request.GET['itm_id']
            sitm = Sale_item.objects.get(id=itm_id)
            sid = str(sitm.iid)
            sl = Sale.objects.get(iid=sid)
            sl.total = sl.total - sitm.amount
            sl.t_total = sl.total * (95.2385 / 100)
            # sl.g_total = sl.t_total * (2.5 / 100)
            sl.q_total -= sitm.qty
            sl.fq_total -= sitm.fqty
            tot = sl.total
            par = Party.objects.get(party_name=sitm.party_name)
            par.balance = par.balance - sitm.amount
            par.save()
            sl.save()
            sitm.delete()
            Log.objects.create(user=request.user, process='Delete Sale update item', reference=sid + ' : ' + str(sl.party_name)+ ' |B: ' + str(sl.party_name.balance))  # Log_added
            data = {'deleted': True, 'tot': tot}
            return JsonResponse(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_sale_update_item',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
def saveSale(request):
    try:
        with transaction.atomic():
            dt = request.GET['date']
            now = timezone.now()
            current_time = now.strftime("%H:%M:%S")
            dt_string = dt + current_time
            fom = "%Y-%m-%d%H:%M:%S"
            dt_object = datetime.datetime.strptime(dt_string, fom)
            od_no = request.GET['od_no']
            prfx = request.GET['pr']
            report = request.GET['report']
            if request.GET['rc'] == '':
                rc = 0
            else:
                rc = float(request.GET['rc'])
            par = Party.objects.get(party_name=Sale.objects.get(iid=(prfx + str(od_no))).party_name)
            sale = Sale.objects.get(s_id=od_no, id_prefix=Prefix.objects.get(prefix=prfx))
            # Check staff sale
            if request.user.groups.filter(name="staff").exists():
                today = datetime.datetime.today().date()
                if sale.date.date() != today and sale.t_type == 'payment' or sale.t_type == 'sale':
                    return HttpResponse('You are not authorized to view the page ')
            sale.date = dt_object
            sale.received = rc
            par.balance -= rc
            sale.balance = par.balance
            sale.report = report
            sale.save()
            lt = Sale.objects.filter(party_name=Party.objects.get(party_name=par.party_name)).latest('date')
            par.updated = lt.date
            par.save()
            data = 1
            Log.objects.create(user=request.user, process='Save Sale', reference=sale.iid + ' : ' + str(sale.party_name)+ ' |B: ' + str(sale.party_name.balance))  # Log_added
    except ObjectDoesNotExist:
        data = 0
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='saveSale',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})

    return HttpResponse(data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def deleteSale(request):
    try:
        with transaction.atomic():
            iid = request.GET['iid']
            print("iid====>",iid)
            sale = Sale.objects.get(iid=iid)
            print("sale===>",sale)
            if sale.t_type != 'order':
                # Check staff sale
                if request.user.groups.filter(name="staff").exists():
                    today = datetime.datetime.today().date()
                    if sale.date.date() != today and sale.t_type == 'payment' or sale.t_type == 'sale':
                        data = 0
                        return HttpResponse(data)
                print("Sale.objects.get(iid=iid).party_name====>",Sale.objects.get(iid=iid).party_name)
                par = Party.objects.get(party_name=Sale.objects.get(iid=iid).party_name)
                print("par==>",par)
                par.balance = (par.balance + sale.received) - sale.total
                if sale.p_type == 'Cash':
                    prof = Profile.objects.get(user=sale.user)
                    prof.balance -= sale.received
                    prof.save()
                sale.delete()
                if Sale.objects.filter(party_name=Party.objects.get(party_name=par.party_name)).exists():
                    lt = Sale.objects.filter(party_name=Party.objects.get(party_name=par.party_name)).latest('date')
                    print("lt===>",lt)
                    par.updated = lt.date
                par.save()
                prfx = Prefix.objects.get(used='sale', active=True)
                max = Sale.objects.filter(id_prefix=sale.id_prefix).aggregate(Max('s_id')).get('s_id__max')
                # if sale.s_id == prfx.last_id:
                #     print("last id =",prfx.last_id)
                if max is None:
                    max = 0
                prfx.last_id = max
                prfx.save()
                data = 1
                Log.objects.create(user=request.user, process='Delete Sale', reference=iid + ' : ' + str(par.party_name)+ ' |B: ' + str(par.balance))  # Log_added
    except ObjectDoesNotExist:
        data = 1
        print('errorrr')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='deleteSale',
            reference = err_descrb
        )
        data = {'code':'500', 'error':'Something went wrong!'}
    return HttpResponse(data)


@login_required(login_url='login')
def edit_invoice(request):
    inv_no = request.GET['inv_no']
    inv_prefix = request.GET['inv_prefix']
    iid = request.GET['iid']
    n_iid = inv_prefix + str(inv_no)
    data = 0
    if iid != n_iid:
        if Sale.objects.filter(iid=n_iid).exists():
            data = 1
    return HttpResponse(data)


# PPPPPPPPPPPPPPPPPPPayment

@login_required(login_url='login')
def take_payment(request):
    try:
        with transaction.atomic():
            if Prefix.objects.filter(used='payment', active=True).exists():
                pr = Prefix.objects.get(used='payment', active=True)
                prefix = pr.prefix
                last_id = Sale.objects.filter(id_prefix=Prefix.objects.get(prefix=prefix)).aggregate(Max('s_id')).get(
                    's_id__max')
                if last_id is None:
                    last_id = 0
            else:
                prefix = '#'
                last_id = 0
                Prefix.objects.create(prefix=prefix, last_id=int(last_id), used='payment', active=True)
            path = '/home'
            new_rp_no = last_id + 1
            party = Party.objects.all()
            party_ob = {'party_name': '---Select a party---'}
            if request.GET.get('party') is not None:
                pname = request.GET.get('party')
                party_ob = {'party_name': Party.objects.get(id=pname).party_name,
                            'balance': Party.objects.get(id=pname).balance}
                pid = pname
                path = '?data=' + str(pid)
            pay = {'amount': ''}
            if request.method == 'POST':
                path = request.POST['path']
                ptype = request.POST['type']
                amount = float(request.POST['amount'])
                rp_no = request.POST['rp_no']
                iid = prefix + str(rp_no)
                p_name = request.POST['s_party']
                now = timezone.now()
                current_time = now.strftime("%H:%M:%S")
                dt_string = request.POST['date'] + current_time
                fom = "%Y-%m-%d%H:%M:%S"
                dt_object = datetime.datetime.strptime(dt_string, fom)
                party = Party.objects.get(party_name=p_name)
                party.balance -= amount
                lt = Sale.objects.filter(party_name=Party.objects.get(party_name=p_name)).latest('date')
                party.updated = lt.date
                Sale.objects.create(s_id=rp_no, id_prefix=Prefix.objects.get(prefix=prefix), iid=iid,
                                    party_name=Party.objects.get(party_name=p_name), date=dt_object, party_type=party.type,
                                    t_type='payment', total=0, received=amount, p_type=ptype,
                                    balance=party.balance, user=User.objects.get(username=request.user.username))
                
                party.save()
                if ptype == 'Cash':
                    prof = Profile.objects.get(user=request.user)
                    prof.balance += amount
                    prof.save()
                Log.objects.create(user=request.user, process='Take Payment', reference=iid + ' : ' + p_name+ ' |Amt: '+ str(amount) +   ' |CB: ' + str(party.balance))  # Log_added
                if path == '/home':
                    return redirect(path)
                else:
                    return redirect(reverse('party_view') + path)
            if request.user.groups.filter(name="admin").exists():
                return render(request, 'adm/take_payment.html',
                            {'party': party, 'party_ob': party_ob, 'rp_no': new_rp_no, 'pay': pay, 'path': path})
            else:
                party = Party.objects.exclude(Q(type='Distribution') | Q(type='General'))
                return render(request, 'staff/take_payment.html',
                            {'party': party, 'party_ob': party_ob, 'rp_no': new_rp_no, 'pay': pay, 'path': path})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='take_payment',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})

@login_required(login_url='login')
def view_bal(request):
    try:
        s_party = request.GET['s_party']
        part = Party.objects.get(party_name=s_party)
        bal = part.balance
        place = part.address
        phone = part.phone
    except:
        bal = 'none'
        place = ''
        phone = ''
    data = {'bal': bal, 'place': place, 'phone': phone}
    return JsonResponse(data)


@login_required(login_url='login')
def pro_price(request):
    try:
        sel = request.GET['select']
        party = request.GET['party']
        product = Products.objects.get(pname=sel)
        party_ob = Party.objects.get(party_name=party)
        if party_ob.type == 'Retail':
            price = product.r_price
        elif party_ob.type == 'Hotel':
            price = product.h_price
        elif party_ob.type == 'Distribution':
            price = product.d_price
        elif party_ob.type == 'Wholesale':
            price = product.w_price
        else:
            price = 'Update party type First!'
        try:
            sale = Sale_item.objects.filter(party_name=Party.objects.get(party_name=party),
                                            p_name=product).order_by('-id')[0]
            l_price = sale.price
        except:
            l_price = price
        data = {'price': price, 'l_price': l_price}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='pro_price',
            reference = err_descrb
        )
        # return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})
        data = {'price': 'none'}
    return JsonResponse(data)

@login_required(login_url='login')
def get_party_obj(request):
    try:
        party = request.GET['party']
        data = Party.objects.get(party_name=party)
        data = {'phone':data.phone, "address":data.address}
    except:
        data = 0
    print("dataa===>",data)
    
    return JsonResponse(data)

@login_required(login_url='login')
def add_report(request):
    try:
        with transaction.atomic():
            party_name = request.GET['select']
            rsn = request.GET['rsn']
            disc = request.GET['disc']
            cat = request.GET['cat']
            Report.objects.create(
                party_name=Party.objects.get(party_name=party_name),
                report=rsn,
                category=cat,
                disc=disc
            )
            Log.objects.create(user=request.user, process='Add Report', reference=party_name)  # Log_added
            return HttpResponse('success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_report',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
def add_expense(request):
    try:
        with transaction.atomic():
            exp = request.GET['exp']
            amount = request.GET['amount']
            disc = request.GET['disc']
            try:
                dt = request.GET['date']
            except:
                dt = datetime.datetime.now()
            if dt == '':
                dt = datetime.datetime.now()
            Expense.objects.create(
                user=request.user,
                expense=exp,
                amount=amount,
                disc=disc,
                date=dt
            )
            profile = Profile.objects.get(user=request.user)
            profile.balance -= float(amount)
            profile.save()
            Log.objects.create(user=request.user, process='Add Expense', reference=exp + '\t Rs:' + str(amount)+ ' |CB: ' + str(profile.balance))  # Log_added
            return HttpResponse('success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_expense',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def take_collection(request):
    try:
        with transaction.atomic():
            staf = request.GET['staff']
            amount = float(request.GET['amount'])
            p_type = request.GET['p_type']
            emp = User.objects.get(username=staf)
            Collection.objects.create(
                user=emp,
                amount=amount,
                p_type=p_type,
                receiver=request.user.username
            )
            prof = Profile.objects.get(user=emp)
            prof.balance -= amount
            prof.save()
            msg = 'Successfully collected ' + str(amount) + ' Rupees from ' + str(staf)
            messages.success(request, msg)
            Alert.objects.create(
                heading='Collection Received', body=str(amount) + ' Rupees received to :' + str(request.user.username) + '\nCheck your balance : https://jesyfoods.com/MyAccount',
                user=emp)
            Log.objects.create(user=request.user, process='Take Collection', reference=str(staf) + '\tRs:' + str(amount)+ ' |CB: ' + str(prof.balance)) # Log_added
            return HttpResponse('success')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='takeCollection',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
def price_list(request):
    product = Products.objects.filter(active=True).order_by('pname')
    price = 'Retail Price'
    size = 'All'
    if request.method == 'POST':
        size = request.POST['size']
        price = request.POST['price']
        print('size =',size)
        print('price =',price)
        product = Products.objects.filter(size=size, active=True).order_by('pname')
        if size == 'All':
            product = Products.objects.filter(active=True).order_by('pname')
    return render(request, 'staff/price_list.html', {'products': product, 'price': price, 'size': size})


@login_required(login_url='login')
def view_orders(request):
    try:
        today = datetime.date.today()
        odr = Sale.objects.filter(t_type='order').order_by('date')
        pr = Products.objects.all().order_by('pname')
        products = []
        for i in pr:
            products.append(i.pname)
        count = {}
        for j in products:
            count[j] = 0
        for i in odr:
            itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=i.iid))

            for j in itm:
                for k in pr:
                    if str(k.pname) == str(j.p_name):
                        count[k.pname] += j.qty
                    else:
                        pass
        total = 0
        no = 0
        for i in odr:
            total += i.total
            no += 1
        if request.user.groups.filter(name="admin").exists():
            return render(request, 'adm/orders.html', {'odr': odr, 'today': today, 'ct': count, 'total': total, 'no': no})
        else:
            return render(request, 'staff/orders.html', {'odr': odr, 'today': today, 'total': total, 'no': no})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='view_orders',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def add_party(request):
    try:
        with transaction.atomic():
            if request.method == 'POST':
                if request.FILES.get('image') is None:
                    image= 'shope_profile.jpg'
                else:
                    image=request.FILES['image']
                if request.POST.get('party_type'):
                    party_type = request.POST['party_type']
                else:
                    party_type = "seller"
                Party.objects.create(
                    party_name=request.POST['name'],
                    address=request.POST['address'],
                    phone=request.POST['phone'],
                    owner=request.POST['owner'],
                    GSTIN=request.POST['gst'],
                    whatsapp=request.POST['whatsapp'],
                    email=request.POST['email'],
                    category=request.POST['category'],
                    type=request.POST['type'],
                    account=request.POST['account'],
                    route=request.POST['route'],
                    image=image,
                    party_type=party_type,
                    user=request.user
                )
                messages.success(request, 'Successfully added a new party!')
                Log.objects.create(user=request.user, process='Add Party', reference=request.POST['name'])  # Log_added
                return redirect('home')
            if request.user.groups.filter(name="admin").exists():
                return render(request, 'adm/add_party.html')
            else:
                return render(request, 'staff/add_party.html')
    except IntegrityError:
        messages.info(request, 'ERROR: Party name already exists!')
        if request.user.groups.filter(name="admin").exists():
            return render(request, 'adm/add_party.html')
        else:
            return render(request, 'staff/add_party.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_party',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
def pdf_view(request):
    try:
        if request.GET.get('data') is not None:
            sett = Settings.objects.get(user=request.user)
            sale_id = request.GET.get('data')
            sale = Sale.objects.get(id=sale_id)
            sale_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid))
            count = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid)).count()
            count = sett.inv_pdf_column - count

        lt = Sale.objects.filter(party_name=sale.party_name, t_type='sale').latest('date')
        cb = sett.inv_pdf_balance
        rtn = None
        # if sale.party_name.balance > sale.total:
        #     ob = sale.party_name.balance - sale.total
        # elif sale.party_name.balance == sale.total:
        #     ob = 0
        # else:
        #     ob = sale.party_name.balance
        ob =  sale.party_name.balance - sale.total 
        if sale.t_type == 'payment':
            words = num2words(sale.received, lang='en_IN')
            template_path = 'adm/payment_pdf_a5.html'
        else:
            words = num2words(sale.total, lang='en_IN')
            if sale.t_type == 'return':
                # rtn = Return.objects.get(iid=sale)
                words = num2words(-sale.total, lang='en_IN')
            template_path = 'adm/sale_pdf_a5.html'
        cl = count  # 14
        gap = list(range(1, cl))
        q_total = 0
        g_total = 0
        fq_total = 0
        for i in sale_itm:
            q_total += i.qty
            g_total += i.gst
            fq_total += i.fqty
        context = {'sale': sale, 'itm': sale_itm, 'gap': gap, 'words': words, 'ob': ob, 'cb': cb, 'q_total': q_total,
                'g_total': g_total, 'fq_total': fq_total}

        response = HttpResponse(content_type='application/pdf')

        partyname = str(sale.party_name).replace(" ", "_").replace(",", "_").replace(".", "_").replace("&", "_")
        file = partyname + '_' + str(sale.iid) + '_' + str(sale.date.strftime('%m_%d_%y'))
        # file = str(sale.party_name) + '_' + str(sale.iid) + '_' + str(sale.date.strftime('%m_%d_%y'))
        response['Content-Disposition'] = 'filename=' + file + ''

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='pdf_view',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def gst_report_pdf(request):
    try:
        t_value = 0
        t_gst = 0
        t_tvalue = 0
        rt_value = 0
        rt_gst = 0
        rt_tvalue = 0
        sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m").date()
        ed = datetime.datetime.strptime(request.POST['ed'], "%Y-%m").date()
        ed = (ed.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        
        sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed]).order_by('s_id')
        rtn = Sale.objects.filter(t_type='return', date__date__range=[sd, ed]).order_by('s_id')
        for i in sale:
            t_value += i.total
            t_tvalue += i.t_total
            t_gst += (i.total - i.t_total) / 2
        for i in rtn:
            rt_value += i.total
            rt_tvalue += i.t_total
            rt_gst += (i.total - i.t_total) / 2
        template_path = 'adm/gst_report_pdf.html'

        total = {'t_value': t_value, 't_tvalue': t_tvalue, 't_gst': t_gst}
        rtotal = {'t_value': -rt_value, 't_tvalue': -rt_tvalue, 't_gst': -rt_gst}
        context = {'sale': sale, 'total': total, 'rtn': rtn, 'rtotal':rtotal}

        response = HttpResponse(content_type='application/pdf')

        file = "GSTR_REPORT_" + str(sd) + '_to_' + str(ed)
        response['Content-Disposition'] = 'filename=' + file + ''

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='gst_report_pdf',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def daybook_pdf(request):
    try:
        date = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
        sale = Sale.objects.filter(t_type='sale', date__date=date)
        template_path = 'adm/daybook_pdf.html'
        context = {'date': date, 'sale': sale}
        response = HttpResponse(content_type='application/pdf')
        file = "File_Name"
        response['Content-Disposition'] = 'filename=' + file + ''
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='daybook_pdf',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


# def PDF_FORMATE(request):
#     template_path = 'adm/gst_report_pdf.html'
#     context = {}
#     response = HttpResponse(content_type='application/pdf')
#     file = "File_Name"
#     response['Content-Disposition'] = 'filename=' + file + ''
#     template = get_template(template_path)
#     html = template.render(context)
#
#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#         html, dest=response)
#     # if error then show some funy view
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response


@login_required(login_url='login')
def party_statement_item_pdf(request):
    try:
        party = Party.objects.get(party_name=request.POST['party'])
        if request.POST.get('check') is None:
            sale_itm = None
        else:
            sale_itm = Sale_item.objects.filter(party_name=party)
        t_value = 0
        t_gst = 0
        t_tvalue = 0
        sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
        ed = datetime.datetime.strptime(request.POST['ed'], "%Y-%m-%d").date()
        print("ssssssssssd=",sd)
        print("esssssssssd=",ed)
        # ed = datetime.datetime(ed.year, ed.month + 1, 1) - datetime.timedelta(seconds=1)
        ed = (ed.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        
        print("eessssssssd=",ed)
        active_process_balance(party, sd, ed)
        sale = Sale.objects.filter(party_name=party, date__date__range=[sd, ed]).order_by('date')
        for i in sale:
            t_value += i.total
            t_tvalue += i.t_total
            t_gst += (i.total - i.t_total) / 2

        template_path = 'adm/party_statement_item_pdf.html'

        total = {'t_value': t_value, 't_tvalue': t_tvalue, 't_gst': t_gst}
        context = {'party': party, 'sd': sd, 'ed': ed, 'sale': sale, 'sale_itm': sale_itm, 'total': total}

        response = HttpResponse(content_type='application/pdf')

        partyname = str(party.party_name).replace(" ", "_").replace(",", "_").replace(".", "_").replace("&", "_")
        file = partyname + '_' + str(sd.strftime('%m_%d_%y')) + '_to_' + str(
            ed.strftime('%m_%d_%y'))
        response['Content-Disposition'] = 'filename=' + file + ''

        template = get_template(template_path)

        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='party_statement_item_pdf',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
def invoice_view(request):
    try:
        if request.GET.get('id') is not None:
            path = 1
            sale_id = request.GET.get('id')
        else:
            path = 0
            sale_id = request.GET.get('data')
        sale = Sale.objects.get(id=sale_id)
        sale_itm = Sale_item.objects.filter(iid=Sale.objects.get(iid=sale.iid))
        g_total = 0
        for i in sale_itm:
            g_total += i.gst
        data = {'sale': sale, 'itm': sale_itm, 'g_total': g_total, 'path': path}
        return render(request, 'staff/invoice_view.html', data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='invoice_view',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
def daybook(request):
    try:
        payment = True
        order = False
        sl = False
        total = 0
        cash = 0
        sd = timezone.now().date()
        # ed = timezone.now().date() + datetime.timedelta(days=1)

        if request.user.groups.filter(name="admin").exists():
            sale = Sale.objects.filter(t_type='payment', date__date=sd)
            for i in sale:
                total += i.received
                if i.p_type == 'Cash':
                    cash += i.received
            # ed = sd
            if request.method == 'POST':
                total = 0
                cash = 0
                if request.POST.get('sd') == '':
                    return redirect('daybook')
                sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
                if request.POST.get('payment') is not None:
                    if request.POST.get('order') is not None:
                        sl = True
                        sale = Sale.objects.filter(Q(t_type='payment') | Q(t_type='sale'), Q(date__date=sd))
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                    else:
                        payment = True
                        sl = False
                        sale = Sale.objects.filter(t_type='payment', date__date=sd)
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                else:
                    if request.POST.get('order') is not None:
                        payment = False
                        sl = True
                        sale = Sale.objects.filter(t_type='sale', date__date=sd)
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                    else:
                        payment = True
                        sale = Sale.objects.filter(t_type='payment', date__date=sd)
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                ed = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
            # sale = Sale.objects.filter(t_type='payment', date__lte=("2022-08-26"), date__gte=("2022-08-26"))
            data = {'sale': sale, 'sd': sd, 'payment': payment, 'sl': sl, 'total': total, 'cash': cash}
            print('sale=', sale)
            return render(request, 'adm/daybook.html', data)
        else:
            sale = Sale.objects.filter(Q(t_type='payment'), Q(date__date=sd), Q(party_type='Retail') |
                                    Q(party_type='Wholesale') | Q(party_type='Hotel'))
            for i in sale:
                total += i.received
                if i.p_type == 'Cash':
                    cash += i.received
            # ed = sd
            if request.method == 'POST':
                total = 0
                cash = 0
                if request.POST.get('sd') == '':
                    return redirect('daybook')
                sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m-%d").date()
                if request.POST.get('payment') is not None:
                    if request.POST.get('order') is not None:
                        sl = True
                        print("STATUS = P & O")
                        sale = Sale.objects.filter(Q(t_type='payment') | Q(t_type='sale'), Q(date__date=sd),
                                                Q(party_type='Retail') | Q(party_type='Wholesale') | Q(
                                                    party_type='Hotel'))
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                    else:
                        payment = True
                        sl = False
                        print("STATUS = P ")
                        sale = Sale.objects.filter(Q(t_type='payment'), Q(date__date=sd), Q(party_type='Retail') |
                                                Q(party_type='Wholesale') | Q(party_type='Hotel'))
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                else:
                    if request.POST.get('order') is not None:
                        payment = False
                        sl = True
                        print("STATUS =  O")
                        sale = Sale.objects.filter(Q(t_type='sale'), Q(date__date=sd), Q(party_type='Retail') |
                                                Q(party_type='Wholesale') | Q(party_type='Hotel'))
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
                    else:
                        payment = True
                        print("STATUS = P ")
                        sale = Sale.objects.filter(Q(t_type='payment'), Q(date__date=sd), Q(party_type='Retail') |
                                                Q(party_type='Wholesale') | Q(party_type='Hotel'))
                        for i in sale:
                            total += i.received
                            if i.p_type == 'Cash':
                                cash += i.received
            # sale = Sale.objects.filter(t_type='payment', date__lte=("2022-08-26"), date__gte=("2022-08-26"))
            data = {'sale': sale, 'sd': sd, 'payment': payment, 'sl': sl, 'total': total, 'cash': cash}
            print('sale=', sale)
            return render(request, 'staff/daybook.html', data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='day_book',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



# def pdf_view(request):
#     if request.GET.get('data') is not None:
#         print('post worked')
#         sale_id = request.GET.get('data')
#
#     sale = Sale.objects.filter(t_type='payment').order_by('-date')
#
#     template_path = 'adm/pdf_view.html'
#     cl = 14
#     gap = list(range(1, cl))
#     print('list====', gap)
#
#     context = {'sale': sale, 'gap': gap}
#
#     response = HttpResponse(content_type='application/pdf')
#
#     response['Content-Disposition'] = 'filename="sale_report.pdf"'
#
#     template = get_template(template_path)
#
#     html = template.render(context)
#
#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#         html, dest=response)
#     # if error then show some funy view
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response
# def pdf_view(request):
#     sale = Sale.objects.filter(t_type='payment').order_by('-date')
#     pdf = render_to_pdf('adm/adm_payments.html')
#     return HttpResponse(pdf, content_type='application/pdf')

@login_required(login_url='login')
def MyAccount(request):
    try:
        if request.method == 'POST':
            if Profile.objects.filter(user=User.objects.get(username=request.user.username)).exists():
                prof = Profile.objects.get(user=User.objects.get(username=request.user.username))
                prof.name = request.POST['name']
                prof.address = request.POST['address']
                prof.phone = request.POST['phone']
                prof.save()
                request.user.email = request.POST['email']
                request.user.save()
            else:
                Profile.objects.create(user=request.user,
                                    name=request.POST['name'],
                                    phone=request.POST['phone'],
                                    address=request.POST['address']
                                    )
        profile = Profile.objects.get(user=User.objects.get(username=request.user.username))
        sale = Sale.objects.filter(date__date=timezone.now().date(), user=request.user, t_type='payment', p_type='Cash')
        today = 0
        today_exp = 0
        for i in sale:
            today += i.received
        exp = Expense.objects.filter(date__date=timezone.now().date(), user=request.user)
        for j in exp:
            today_exp += j.amount
        sale = Sale.objects.filter(date__date=timezone.now().date() - datetime.timedelta(days=1), user=request.user,
                                t_type='payment', p_type='Cash')

        yes = 0
        yes_exp = 0
        for i in sale:
            yes += i.received
        exp = Expense.objects.filter(date__date=timezone.now().date() - datetime.timedelta(days=1), user=request.user)
        for j in exp:
            yes_exp += j.amount

        prev1_d = timezone.now().date() - datetime.timedelta(days=2)
        sale = Sale.objects.filter(date__date=prev1_d, user=request.user, t_type='payment', p_type='Cash')
        prev1 = 0
        prev1_exp = 0
        for i in sale:
            prev1 += i.received
        exp = Expense.objects.filter(date__date=prev1_d, user=request.user)
        for j in exp:
            prev1_exp += j.amount

        collection = Collection.objects.filter(user=request.user).order_by('-date')[:3]
        balance = {'today': today, 'yes': yes, 'prev1': prev1, 'prev1_d': prev1_d, 'collection': collection,
                'today_exp': today_exp,
                'yes_exp': yes_exp, 'prev1_exp': prev1_exp}
        recent = Sale.objects.filter(user=request.user).order_by('-date')[:10]
        return render(request, 'staff/account.html', {'profile': profile, 'recent': recent, 'balance': balance})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='my_account',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
def PasswordChangeDone(request):
    Log.objects.create(user=request.user, process='Password Changed', reference='Success')  # Log_added
    return render(request, 'staff/account.html', {'msg': 'Password Changed SuccessFully'})


@login_required(login_url='login')
def settings(request):
    try:
        set = Settings.objects.get(user=request.user)
        superusers = False
        if User.objects.filter(username=request.user, is_superuser=True).exists():
            superusers = True
        if request.GET.get('data') is not None:
            data = request.GET['data']
            value = bool(request.GET['value'])
            if data == 'order':
                set.home_order = value
                set.save()
            elif data == 'daybook':
                set.home_daybook = value
                set.save()
            elif data == 'credit':
                set.home_credit = value
                set.save()
            elif data == 'sale':
                set.home_sale = value
                set.save()
            elif data == 'expense':
                set.home_expense = value
                set.save()
            elif data == 'inv_view_tax':
                set.inv_view_tax = value
                set.save()
            elif data == 'inv_view_round':
                set.inv_view_round = value
                set.save()
            elif data == 'inv_pdf_round':
                set.inv_pdf_round = value
                set.save()
            elif data == 'inv_pdf_cbalance':
                set.inv_pdf_balance = value
                set.save()
            elif request.GET['value'] == 'column':
                data = request.GET['data']
                set.inv_pdf_column = int(data)
                set.save()
            else:
                print('elseee eeeoewkreed')

        return render(request, 'staff/settings.html', {'sett': set, 'su':superusers})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='settings',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
def view_expense(request):
    try:
        exp = Expense.objects.filter(user=request.user).order_by('-date')
        sel = request.user.username
        if request.method == 'POST':
            if request.POST['val'] == 'all':
                exp = Expense.objects.all().order_by('-date')
                sel = 'All'
            else:
                return redirect('view_expense')
        if request.user.groups.filter(name="admin").exists():
            return render(request, 'adm/view_expense.html', {'exp': exp, 'sel': sel})
        else:
            now = timezone.now()
            year = now.year
            month = now.date() - datetime.timedelta(days=3)
            exp = Expense.objects.filter(user=request.user,date__month=datetime.datetime(now.year, now.month, 1).month, date__year=year).order_by('-date')
            return render(request, 'staff/view_expense.html', {'exp': exp, 'month': month})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='view_expense',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'admin'])
def delete_expense(request):
    try:
        with transaction.atomic():
            dat = timezone.now().date() - datetime.timedelta(days=3)
            id = request.GET['id']
            exp = Expense.objects.get(id=id)
            prof = Profile.objects.get(user=exp.user)
            if exp.date.date() > dat or request.user.groups.filter(name="admin").exists():
                prof.balance += exp.amount
                exp.delete()
                prof.save()
                Log.objects.create(user=request.user, process='Delete Expense', reference=':Rs='+ str(exp.amount)+':CB='+str(prof.balance))  # Log_added + '\tRs:' + str(amount)+ ' |CB: 
            else:
                # return HttpResponse('ERROR: Unauthorized process')
                Log.objects.create(
                    user=request.user,
                    type='Warning',
                    process='delete_expense',
                    reference = 'Access Denied'
                )
                return render(request, 'error.html', {'code':'403', 'error':'Access Denied!'})

            return redirect('view_expense')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_expense',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def employees(request):
    try:
        profile = Profile.objects.all()
        prof = None
        if request.GET.get('data') is not None:
            prof = Profile.objects.get(id=request.GET['data'])
        if request.method == 'POST':
            prof = Profile.objects.get(user=User.objects.get(username=request.POST['user']))
            prof.name = request.POST['name']
            prof.address = request.POST['address']
            prof.position = request.POST['position']
            prof.phone = request.POST['phone']
            prof.salary = request.POST['salary']
            prof.phone_2 = request.POST['phone_2']
            prof.whatsapp = request.POST['whatsapp']
            prof.gpay = request.POST['gpay']
            prof.account = request.POST['account']
            prof.ifsc = request.POST['ifsc']
            prof.branch = request.POST['branch']
            prof.save()
            us = User.objects.get(username=request.POST['user'])
            us.email = request.POST['email']
            us.username = request.POST['username']
            us.save()
            Log.objects.create(user=request.user, process='Update Staff', reference=us.username)  # Log_added
        return render(request, 'adm/view_employees.html', {'profile': profile, 'prof': prof})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='employees',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def view_products(request):
    try:
        products = Products.objects.all().order_by('pname')
        prof = None
        if request.GET.get('data') is not None:
            prof = Products.objects.get(id=request.GET['data'])
        if request.method == 'POST':
            prof = Products.objects.get(id=request.POST['id'])
            prof.pname = request.POST['name']
            prof.size = request.POST['size']
            # if request.POST['hsn'] != '':
            #     prof.HSN = int(request.POST['hsn'])
            prof.barcode = request.POST['barcode']
            if request.POST['mrp'] != '':
                prof.mrp = float(request.POST['mrp'])
            prof.HSN = request.POST['hsn']
            prof.r_price = request.POST['r_price']
            prof.w_price = request.POST['w_price']
            prof.h_price = request.POST['h_price']
            prof.d_price = request.POST['d_price']
            prof.save()
            Log.objects.create(user=request.user, process='Update Product', reference=prof.pname)  # Log_added
        return render(request, 'adm/products.html', {'products': products, 'prof': prof})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='view_products',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



def active_product(request):
    prod = Products.objects.get(id=request.GET['data'])
    value = bool(request.GET['value'])
    prod.active = value
    prod.save()
    Log.objects.create(user=request.user, process='Product Activation', reference=prod.pname)  # Log_added
    return HttpResponse('success')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def active_process(request):
    if request.method == 'POST':
        # PROCESS-1 Add balance to party sale
        # party = Party.objects.all()
        # for i in party:
        #     balance = 0
        #     sale = Sale.objects.filter(party_name=i).order_by('date')
        #     print('SALE#')
        #     for j in sale:
        #         print('saleeee =',j.iid)
        #         if j.t_type == 'sale':
        #             balance = j.balance = balance + (j.total - j.received)
        #             j.save()
        #             print('save sale')
        #         elif j.t_type == 'payment':
        #             balance = j.balance = balance - j.received
        #             j.save()
        #             print('save payment')
        #         else:
        #             print("ELSE WORKED FOR ORDER")
        # messages.success(request, 'Successfully Completed PROCESS-1')
        # END PROCESS-1

        # PROCESS-2 Add t_qty & ft_qty to sale
        # party = Party.objects.all()
        # for i in party:
        #     sale = Sale.objects.filter(t_type='sale', party_name=i).order_by('date')
        #     for j in sale:
        #         q_total = 0
        #         fq_total = 0
        #         try:
        #             sale_itm = Sale_item.objects.filter(iid=j)
        #             for k in sale_itm:
        #                 q_total += k.qty
        #                 fq_total += k.fqty
        #             j.q_total = q_total
        #             j.fq_total = fq_total
        #             j.save()
        #             print('#####')
        #         except ObjectDoesNotExist:
        #             print('################# Something went Wrong #######################')
        # messages.success(request, 'Successfully Completed PROCESS-2')
        # print('################ Successfully Completed PROCESS-2 ##############')
        # END PROCESS-2
        # PROCESS-3 Add party type to  sale
        party = Party.objects.filter(Q(type='Distribution') | Q(type='General'))
        for i in party:
            sale = Sale.objects.all()
            for j in sale:
                if j.party_name == i:
                    j.party_type = i.type
                    j.save()
        messages.success(request, 'Successfully Completed PROCESS-3')
        # END PROCESS-3
    return render(request, 'action_process.html')

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def active_process_balance(par, sd, ed):
    # PROCESS-1 Add balance to party sale
    balance = 0
    sale = Sale.objects.filter(party_name=par, date__date__lte=sd).order_by('date')
    for j in sale:
        if j.t_type == 'sale':
            balance = j.balance = balance + (j.total - j.received)
            # j.save()
        elif j.t_type == 'payment':
            balance = j.balance = balance - j.received
            # j.save()
        else:
            # print("ELSE WORKED FOR ORDER")
            pass
    # messages.success(request, 'Successfully Completed PROCESS-1')
    # END PROCESS-1

    sale = Sale.objects.filter(party_name=par, date__date__range=[sd, ed]).order_by('date')
    for i in sale:
        balance = balance + i.total - i.received
        if i.balance != balance:
            i.balance = balance
            i.save()

    return


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def view_messages(request):
    try:
        report = Report.objects.filter(category='Report').order_by('-date')
        feedback = Report.objects.filter(category='Feedback').order_by('-date')
        msg = Messages.objects.all().order_by('-date')
        count_msg = Messages.objects.all().count()
        # count_rpt = Report.objects.filter(category='Report').count()
        # count_fdb = Report.objects.filter(category='Feedback').count()
        p1 = Paginator(report,30)
        p2 = Paginator(feedback,7)
        p3 = Paginator(msg,3)
        pn1 = request.GET.get('page')
        try:
            page_obj = p1.get_page(pn1)
        except PageNotAnInteger:
            page_obj = p1.get_page(1)
        except EmptyPage:
            page_obj = p1.page(p1.num_pages)
        if request.GET.get('id') is not None:
            mid = request.GET['id']
            report = Report.objects.get(id=mid)
            report.delete()
            Log.objects.create(user=request.user, process='Delete Report', reference=report.party_name)  # Log_added
            return redirect('view_messages')
        if request.method == 'POST':
            report = Report.objects.all()
            report.delete()
            Log.objects.create(user=request.user, process='Delete All Report', reference='clear all')  # Log_added
            return redirect('view_messages')
        if request.GET.get('msg') is not None:
            mid = request.GET['msg']
            msg = Messages.objects.get(id=mid)
            msg.delete()
            Log.objects.create(user=request.user, process='Delete Msg', reference=msg.name)  # Log_added
            return redirect('view_messages')
        return render(request, 'adm/messages.html', {'feedback': feedback, 'msg': msg, 'count_msg': count_msg,'p1_obj':page_obj})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='view_messages',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def gst_report(request):
    try:
        filt = 'This Month'
        now = timezone.now()
        sd = now.month
        year = now.year
        ed = sd
        t_value = 0
        t_gst = 0
        t_tvalue = 0
        rt_value = 0
        rt_gst = 0
        rt_tvalue = 0
        sale = Sale.objects.filter(t_type='sale', date__month=sd, date__year=year)
        rtn = Sale.objects.filter(t_type='return', date__month=sd, date__year=year)
        sd = datetime.datetime(year, sd, 1)
        ed = sd
        if request.method == 'POST':
            type = request.POST['type']
            if type == 'filter':
                filt = request.POST['filter']
                if filt == 'Prev Month':
                    # sd = datetime.datetime(now.year, now.month - 1, 1).month
                    sd = datetime.datetime(now.year, now.month, 1) - relativedelta(months=1)
                    year = sd.year
                    sd = sd.month
                    # year = datetime.datetime(now.year, now.month - 1, 1).year
                    sale = Sale.objects.filter(t_type='sale', date__month=sd, date__year=year)
                    rtn = Sale.objects.filter(t_type='return', date__month=sd, date__year=year)
                    sd = datetime.datetime(year, sd, 1)
                    ed = sd
                elif filt == 'This Month':
                    return redirect('gst_report')
                elif filt == 'This Year':
                    # year = datetime.datetime(now.year, now.month - 1, 1).year
                    sale = Sale.objects.filter(t_type='sale', date__year=year)
                    rtn = Sale.objects.filter(t_type='return', date__year=year)
                    sd = datetime.datetime(year, 1, 1)
                    ed = datetime.datetime(year, 12, 1)
                elif filt == 'This Financial Year':
                    sd = datetime.datetime(year - 1, 4, 1)
                    ed = datetime.datetime(year, 3, 31)
                    sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed])
                    rtn = Sale.objects.filter(t_type='return', date__date__range=[sd, ed])

            elif type == 'date':
                if request.POST.get('sd') == '' or request.POST.get('ed') == '':
                    return redirect('gst_report')
                sd = datetime.datetime.strptime(request.POST['sd'], "%Y-%m").date()
                ed = datetime.datetime.strptime(request.POST['ed'], "%Y-%m").date()
                ed = datetime.datetime(ed.year, ed.month + 1, 1) - datetime.timedelta(seconds=1)
                sale = Sale.objects.filter(t_type='sale', date__date__range=[sd, ed])
                rtn = Sale.objects.filter(t_type='return', date__date__range=[sd, ed])
                filt = "Custom"
        gst_party = []
        for i in sale:
            t_value += i.total
            t_tvalue += i.t_total
            t_gst += (i.total - i.t_total) / 2
            if not i.party_name.GSTIN == '':
                gst_party.append(i.party_name)
        for i in rtn:
            rt_value += i.total
            rt_tvalue += i.t_total
            rt_gst += (i.total - i.t_total) / 2
        gst_party = list(dict.fromkeys(gst_party))
        total = {'t_value': t_value, 't_tvalue': t_tvalue, 't_gst': t_gst}
        rtotal = {'t_value': rt_value, 't_tvalue': rt_tvalue, 't_gst': rt_gst}
        return render(request, 'adm/gst_report.html', {'sale': sale.order_by('s_id'), 'total': total, 'sd': sd, 'ed': ed, 'filter': filt,
                                                    'gst_party': gst_party, 'rtn': rtn.order_by('s_id'), 'rtotal':rtotal})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='gst_report',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_party(request):
    try:
        party = Party.objects.get(id=request.POST['id'])
        if Sale.objects.filter(party_name=party).exists():
            messages.success(request, 'Party cannot delete while sale exists for: ' + party.party_name)
            Log.objects.create(user=request.user, process='Tryed Delete Party', reference=party.party_name+ ' :CB= ' + str(party.balance))  # Log_added
            
        else:        
            messages.success(request, 'Party deleted successfully  for: ' + party.party_name)
            party.delete()
            Log.objects.create(user=request.user, process='Delete Party', reference=party.party_name+ ' :CB= ' + str(party.balance))  # Log_added
        return redirect('home')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_party',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_product(request):
    try:
        product = Products.objects.get(id=request.POST['id'])
        sale = Sale_item.objects.all()
        delete = True
        for i in sale:
            if i.p_name.pname == product.pname:
                delete = False
                messages.success(request, "Can't delete! " + product.pname + ' already in a transaction')
                messages.success(request, 'Check Invoice No. = ' + i.iid.iid + '...etc')
                break
        if delete is True:
            messages.success(request, product.pname + ' deleted successfully')
            product.delete()
            Log.objects.create(user=request.user, process='Delete Product', reference=product.pname)  # Log_added
        return redirect('view_products')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='delete_product',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def log(request):
    filter = None
    search = ''
    if request.method == 'POST':
        search = request.POST['search']
        if request.POST.get('filter') is not None:
            filter = request.POST['filter']
            
        logs = Log.objects.filter(reference__icontains=search,type=filter).order_by('-date')
    else:        
        # logs = Log.objects.filter(date__month=timezone.now().month).order_by('-date')
        logs = Log.objects.all().order_by('-date')
    p = Paginator(logs, 100)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'log': logs, 'search':search,'filter':filter}
    # sending the page object to index.html
    return render(request, 'adm/log.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def data_info(request):
    filter = None
    search = ''
    if request.method == 'POST':
        search = request.POST['search']
        if request.POST.get('filter') is not None:
            filter = request.POST['filter']
            
        info = DataInfo.objects.filter(ip__icontains=search )| DataInfo.objects.filter(hostname__icontains=search).order_by('-date')
    else:        
        # logs = Log.objects.filter(date__month=timezone.now().month).order_by('-date')
        info = DataInfo.objects.all().order_by('-date')
    p = Paginator(info, 100)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        page_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'search':search,'filter':filter}
    # sending the page object to index.html
    return render(request, 'adm/data_info.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def all_transactions(request):
    sale = Sale.objects.filter(date__year=timezone.now().year, date__month=timezone.now().month).order_by('-date')
    return render(request, 'adm/all_transactions.html', {'sale': sale})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_messages(request):
    msg = Messages.objects.all()
    msg.delete()
    Log.objects.create(user=request.user, process='Clear All Messages', reference='Deleted')  # Log_added
    return redirect('view_messages')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff'])
def add_party_account(request):
    if request.GET.get('party') is not None:
        party = Party.objects.get(id=request.GET['party'])
    if request.method == 'POST':
        party = Party.objects.get(id=request.POST['id'])
        party.party_name = request.POST['name']
        party.address = request.POST['add']
        party.phone = request.POST['phone']
        party.email = request.POST['email']
        party.GSTIN = request.POST['gst']
        party.type = request.POST['type']
        party.route = request.POST['route']
        party.owner = request.POST['owner']
        party.category = request.POST['category']
        party.save()
    return render(request, 'staff/add_party_home.html', {'party': party})


@login_required(login_url='login')
def party_home(request):
    return render(request, 'party/home.html')


@login_required(login_url='login')
def view_reports(request):
    try:
        party = Party.objects.all()
        now = timezone.now()
        year = now.year
        reports = Report.objects.filter(date__month=datetime.datetime(now.year, now.month, 1).month, date__year=year).order_by('-date')
        if request.user.groups.filter(name="admin").exists():
            return render(request, 'adm/view_reports.html')
        else:
            dat = timezone.now().date() - datetime.timedelta(days=7)
            if request.GET.get('id') is not None:
                id = request.GET['id']
                rpt = Report.objects.get(id=id)
                if rpt.date.date() > dat:
                    Log.objects.create(user=request.user, process='Delete Report',
                                    reference=str(rpt.party_name) + '\t' + str(rpt.report) + '\t' + str(rpt.disc) )  # Log_added
                    rpt.delete()
                else:
                    return HttpResponse('ERROR: Unauthorized process')
            return render(request, 'staff/view_reports.html', {'reports':reports ,'party':party, 'dat':dat})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='view_reports',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})


@login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def add_alert(request):
    alert = Alert.objects.all()
    if request.user.groups.filter(name="admin").exists():
        if request.method == 'POST':
            User = get_user_model()
            users = User.objects.all()
            for i in users:
                Alert.objects.create(heading=request.POST['head'], body=request.POST['body'], user=i)
    if request.GET.get('id') is not None:
        alt = Alert.objects.get(id=request.GET.get('id'))
        alt.delete()
    return render(request, 'adm/add_alert.html', {'alert': alert})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def daily_graph(request):
    try:
        graph = 1
        labels = []
        data = []
        ld = Sale.objects.filter(t_type='sale').last().date.date()
        tot_day = (ld.replace(month = ld.month % 12 +1, day = 1)-datetime.timedelta(days=1)).day
        print('day--=',tot_day)
        for i in range(1, tot_day+1):
            dt = (datetime.datetime(ld.year, ld.month, i)).date()
            labels.append(str(dt.strftime("%d %a")))
            d_sale = 0
            sale = Sale.objects.filter(t_type='sale', date__date=dt)
            for j in sale:
                d_sale += j.total
            data.append(d_sale)

        context = {'labels': labels, 'data': data, 'graph':graph}
        return render(request, 'adm/sale_graph.html', context)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='daily_graph',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def month_graph(request):
    try:
        graph = 2
        fd = Sale.objects.filter(t_type='sale').first().date.date()
        ld = Sale.objects.filter(t_type='sale').last().date.date()
        tot_m = (ld.year - fd.year) * 12 + ld.month - fd.month
        fm = ld.month
        add = ld + relativedelta(months=2)

        labels = []
        data = []
        for i in range(tot_m+1):
            now_m = fd + relativedelta(months=i)
            text = datetime.datetime(now_m.year, now_m.month, 1).strftime('%B')
            labels.append(text)

            m_sale = 0
            sale = Sale.objects.filter(t_type='sale', date__year=now_m.year, date__month=now_m.month)
            for j in sale:
                m_sale += j.total
            data.append(m_sale)
            # print('m_sale: ', data)
            # print('month =',now_m.month,' Year=',now_m.year)

        context = {'labels': labels, 'data': data, 'graph':graph}
        return render(request, 'adm/sale_graph.html', context)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='month_graph',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def all_reports(request):
    context = {}
    return render(request, 'adm/all_reports.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product_report(request):
    now = timezone.now()
    year = now.year
    sd = datetime.datetime(now.year, now.month, 1).date()
    ed = (datetime.datetime(now.year, now.month, 1).replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
    print("sd=====",sd)
    print("ed=====",ed)
    products = Products.objects.filter(active=True)
    sales = (Sale.objects.filter(t_type='sale',date__date__gte=sd, date__date__lte=ed).values_list('iid'))
    print("sales===",sales)
    data = Sale_item.objects.filter(iid__iid__in=sales)
    print("data===",data)
    result = []
    xValues = []
    yValues = []
    for i in products:
        # result.append()
        qty = 0
        amount = 0
        avg_price = '-'
        for j in data:
            if str(j.p_name) == str(i.pname):
                qty += j.qty
                amount += j.amount
        if i.size == '100g':
            qty_kg = qty/10
        elif i.size == '50g':
            qty_kg = qty/20
        elif i.size == '250g':
            qty_kg = qty/4
        elif i.size == '500g':
            qty_kg = qty/2
        else:
            qty_kg = qty
        if not qty == 0:
            avg_price = amount/qty_kg  
        result.append(
            {'product':i.pname, 'size':i.size, 'qty':qty, 'qty_kg':qty_kg, 'avg_price':avg_price, 'amount':amount}
        )
        xValues.append(i.pname)
        yValues.append(qty_kg)
    print("result==",result)
    result = sorted(result, key=lambda d: d['qty_kg'], reverse=True) 
    print("result==",result)

    context = {'result':result, 'xValues':xValues, 'yValues':yValues}
    return render(request, 'adm/product_graph.html', context)

def updation_process(request):
    from django.core.cache import cache

    # ...
    cache.delete('http://127.0.0.1:8000/')
    context = {}
    return render(request, 'updation.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def add_purchase(request):
    try:
        with transaction.atomic():
            # Log.objects.create(process='test for atomic3')
            if Prefix.objects.filter(used='purchase', active=True).exists():
                pr = Prefix.objects.get(used='purchase', active=True)
                prefix = pr.prefix
                last_id = Sale.objects.filter(id_prefix=Prefix.objects.get(prefix=prefix)).aggregate(Max('s_id')).get(
                    's_id__max')
                if last_id is None:
                    last_id = 0
            else:
                prefix = 'PI'
                last_id = 0
                Prefix.objects.create(prefix=prefix, last_id=int(last_id), used='purchase', active=True)
            new_s_no = last_id + 1
            dt = datetime.date.today()
            
            products = Products.objects.all()
            party = Party.objects.filter(Q(party_type='buyer')|Q(party_type='both'))
            party_ob = {'party_name': '-----Select a Party-----'}
            
            ob = 0
            cb = 0
            if request.method == 'POST':
                s_party = request.POST['s_party']
                party_ob = Party.objects.get(party_name=Party.objects.get(party_name=s_party))
                cb = ob = party_ob.balance
        return render(request, 'adm/add_purchase.html', {'product':products,"new_s_no":new_s_no,"dt":dt,"party":party,"party_ob":party_ob})
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + '\n' + str(exc_obj) + '\n' + str(fname) + str(exc_tb.tb_lineno)
        Log.objects.create(
            user=request.user,
            type='Error',
            process='add_purchase',
            reference = err_descrb
        )
        return render(request, 'error.html', {'code':'500', 'error':'Something went wrong!'})






def autocomplete(request):
    if 'term' in request.GET:
        qs = Party.objects.filter(Q(party_name__icontains=request.GET.get('term')),Q(party_type='buyer')|Q(party_type='both'))
        titles = list()
        for i in qs:
            titles.append(i.party_name)
        print("titles=",titles)
        if len(titles)==0:
            titles.append({'label':"No results found",'value':''})
            
        return JsonResponse(titles, safe=False)
    return render(request, 'adm/add_purchase.html')


def dataInfo(request):
    print("helo>>>>>>>>>>>>>>>>>>>>>>>")
    details = request.GET.get('debug')
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    DataInfo.objects.create(
        ip = ip,
        hostname = hostname,
        details = str('From Decorators\n\n') + str(details)
    )
    return HttpResponse('success')



@login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
def activity_log(request):
    filter = "Information"
    if request.user.groups.filter(name="admin").exists():
        search = ''
        if request.method == 'POST':
            search = request.POST['search']
            # if request.POST.get('filter') is not None:
            #     filter = request.POST['filter']
                
            logs = Log.objects.filter(reference__icontains=search,type=filter).order_by('-date')
        else:        
            # logs = Log.objects.filter(date__month=timezone.now().month).order_by('-date')
            logs = Log.objects.filter(type=filter).order_by('-date')
        p = Paginator(logs, 100)  # creating a paginator object
        # getting the desired page number from url
        page_number = request.GET.get('page')
        try:
            page_obj = p.get_page(page_number)  # returns the desired page object
        except PageNotAnInteger:
            # if page_number is not an integer then assign the first page
            page_obj = p.page(1)
        except EmptyPage:
            # if page is empty then return last page
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj, 'log': logs, 'search':search,'filter':filter}
        return render(request, 'adm/activity_log.html', context)
    else:
        logs = Log.objects.filter(user=request.user,type=filter).order_by('-date')[:100]
        return render(request, 'staff/activity_log.html', {"logs":logs})