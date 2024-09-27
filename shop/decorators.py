from django.shortcuts import redirect

# a decorator for admin and superuser only
def admin_only(func):
    def wrapper(request,*args,**kwargs):
        group=None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'admin' or request.user.is_superuser:
            return func(request,*args,**kwargs)
        return redirect('shop')
    return wrapper

# a decorator that only accept hx requests 
def htmx_request_only(redirect_url=""):
    def admin_only(func):
        def wrapper(request,*args,**kwargs):
            if request.headers.get('HX-Request') or request.user.is_superuser or request.headers.get("fetch") == 'yes':
                return func(request,*args,**kwargs)
            else:
                return redirect(redirect_url)
        return wrapper
    return admin_only