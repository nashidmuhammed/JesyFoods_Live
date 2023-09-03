from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import MyPasswordChangeForm

# from .views import PasswordsChangeView

urlpatterns = [
    path('', views.index, name='index'),
    path('products', views.products, name='products'),
    path('about', views.about, name='about'),
    path('tasty_hub', views.tasty_hub, name='tasty_hub'),
    path('contact', views.contact, name='contact'),
    path('faq', views.faq, name='faq'),


    path('admin_panel', views.admin_panel, name='admin_panel'),
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),


    path('reset_password',
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
         name="reset_password"),
    path('reset_password_sent',
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_send.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"),
         name="password_reset_confirm"),
    path('reset_password_complete',
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),
         name="password_reset_complete"),


    path('change_password',
         auth_views.PasswordChangeView.as_view(
             template_name='staff/change_password.html',
             success_url=reverse_lazy('PasswordChangeDone'),
             form_class=MyPasswordChangeForm
         )),
    path('PasswordChangeDone', views.PasswordChangeDone, name='PasswordChangeDone'),
    path('register', views.registerPage, name='registerPage'),
#     path('autocomplete', views.autocomplete, name='autocomplete '),
    path('home', views.home, name='home'),
    path('autocomplete', views.autocomplete, name='autocomplete'),
    path('admin_panel', views.admin_panel, name='admin_panel'),
    path('sale_report', views.sale_report_new, name='sale_report_new'),
    path('sale_report_filter', views.sale_report_filter, name='sale_report_filter'),
    path('sale_report_date', views.sale_report_date, name='sale_report_date'),
#     path('payments', views.payments, name='payments'),
    path('payments', views.payments_new, name='payments_new'),
    path('party_statement', views.party_statement, name='party_statement'),
    path('add_sale', views.add_sale, name='add_sale'),
    path('saveSale', views.saveSale, name='saveSale'),
    path('deleteSale', views.deleteSale, name='deleteSale'),
    path('deleteOrder', views.deleteOrder, name='deleteOrder'),
    path('add_order', views.add_order, name='add_order'),
    path('pro_price', views.pro_price, name='pro_price'),
    path('add_sale_item', views.add_sale_item, name='add_sale_item'),
    path('add_order_item', views.add_order_item, name='add_order_item'),
    path('edit_sale_item', views.edit_sale_item, name='edit_sale_item'),
    path('delete_sale_item', views.delete_sale_item, name='delete_sale_item'),
    path('delete_order_item', views.delete_order_item, name='delete_order_item'),
    # path('add_item',views.add_item,name='add_item'),
    # path('del_order',views.del_order,name='del_order'),
    path('add_report', views.add_report, name='add_report'),
    # path('edit_item',views.edit_item,name='edit_item'),
    # path('delete_item',views.delete_item,name='delete_item'),
    path('take_payment', views.take_payment, name='take_payment'),
    path('view_bal', views.view_bal, name='view_bal'),
    path('view_orders', views.view_orders, name='view_orders'),
    # path('view_collection',views.view_collection,name='view_collection'),
    # path('del_payment',views.del_payment,name='del_payment'),
    path('add_party', views.add_party, name='add_party'),
    path('delete_party', views.delete_party, name='delete_party'),
    path('delete_product', views.delete_product, name='delete_product'),
    path('add_product', views.add_product, name='add_product'),
    path('OrderToSale', views.OrderToSale, name='OrderToSale'),
    path('update_sale', views.update_sale, name='update_sale'),
    path('edit_invoice', views.edit_invoice, name='edit_invoice'),
    path('party_report', views.party_report, name='party_report'),
    path('party_view', views.party_view, name='party_view'),
    path('pdf_view', views.pdf_view, name='pdf_view'),
    path('delete_sale_update_item', views.delete_sale_update_item, name='delete_sale_update_item'),
    path('invoice_view', views.invoice_view, name='invoice_view'),
    path('daybook', views.daybook, name='daybook'),
    path('party_statement_date', views.party_statement_date, name='party_statement_date'),
    path('party_statement_filter', views.party_statement_filter, name='party_statement_filter'),
    path('MyAccount', views.MyAccount, name='MyAccount'),
    path('price_list', views.price_list, name='price_list'),
    path('add_expense', views.add_expense, name='add_expense'),
    path('view_expense', views.view_expense, name='view_expense'),
    path('delete_expense', views.delete_expense, name='delete_expense'),
    path('settings', views.settings, name='settings'),
    path('employees', views.employees, name='employees'),
    path('view_products', views.view_products, name='view_products'),
    path('take_collection', views.take_collection, name='take_collection'),
    path('active_product', views.active_product, name='active_product'),
    path('view_messages', views.view_messages, name='view_messages'),
    path('gst_report', views.gst_report, name='gst_report'),
    path('all_transactions', views.all_transactions, name='all_transactions'),
    path('gst_report_pdf', views.gst_report_pdf, name='gst_report_pdf'),
    path('daybook_pdf', views.daybook_pdf, name='daybook_pdf'),
    path('delete_messages', views.delete_messages, name='delete_messages'),
    path('party_statement_item_pdf', views.party_statement_item_pdf, name='party_statement_item_pdf'),
    path('add_party_account', views.add_party_account, name='add_party_account'),
    path('view_reports', views.view_reports, name='view_reports'),
    path('sale_return', views.sale_return, name='sale_return'),
    path('edit_return', views.edit_return, name='edit_return'),
    path('month_graph', views.month_graph, name='month_graph'),
    path('daily_graph', views.daily_graph, name='daily_graph'),
    path('activity_log', views.activity_log, name='activity_log '),
    path('dataInfo', views.dataInfo, name='dataInfo'),
    # For Admin USe
    path('active_process', views.active_process, name='active_process'),
    path('active_process_balance', views.active_process_balance, name='active_process_balance'),
    path('log', views.log, name='log'),
    path('data_info', views.data_info, name='data_info'),
    path('add_alert', views.add_alert, name='add_alert'),
    path('all_reports', views.all_reports, name='all_reports'),
    path('updation_process', views.updation_process, name='updation_process '),
    path('add_purchase', views.add_purchase, name='add_purchase '),
    path('get_party_obj', views.get_party_obj, name='get_party_obj '),
#     path('srh', views.autocomplete, name='srh '),

    # For Party  
    path('party_home', views.party_home, name='party_home'),
    
    # Reports
    path('product_report', views.product_report, name='product_report'),
]
