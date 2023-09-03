from django.http import HttpResponse
from django.shortcuts import redirect ,render
from sale_order.models import Log, DataInfo


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # return HttpResponse('You are not authorized to view the page')
                Log.objects.create(
                    user=request.user,
                    type='Warning',
                    process= str(view_func),
                    reference = 'Access Denied'
                )
                return render(request, 'error.html', {'code':'403', 'error':'Access Denied'})
        return wrapper_func
    return decorator


#def admin_only(view_func):
#    def wrapper_func(request, *args, **kwargs):
#        group = None
#        if request.user.groups.exists():
#            group = request.user.groups.all()[0].name

#        if group == 'staff':
#            return redirect('user-page')

#        if group == 'admin':
#            return view_func(request, *args, **kwargs)

#    return wrapper_func
