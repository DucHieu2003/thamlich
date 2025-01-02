from django.http import HttpResponse
from django.shortcuts import redirect

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Not authorized')
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        # Kiểm tra nếu user là superuser
        # if request.user.is_superuser:
        #     return view_func(request, *args, **kwargs)  # Cho phép truy cập

        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name  

        print(group)  

        if group == 'customer':  
            return redirect('quanli_dskb')  

        if group == 'admin':  
            return view_func(request, *args, **kwargs)  
        
        
        return HttpResponse('Bạn không có quyền truy cập trang này.', status=403)
    
    return wrapper_function

def admincus_only(view_func):
    def wrapper_function1(request, *args, **kwargs):
        # Kiểm tra nếu user là superuser
        # if request.user.is_superuser:
        #     return view_func(request, *args, **kwargs)  # Cho phép truy cập

        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name  

        print(group)  

        if group == 'customer':  
            return view_func(request, *args, **kwargs)  

        if group == 'admin':  
            return view_func(request, *args, **kwargs)  
        
        
        return HttpResponse('Bạn không có quyền truy cập trang này.', status=403)
    
    return wrapper_function1
