from django.http import HttpResponseRedirect


def auth_required(func):
    def impl(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/auth")
        return func(request)
    return impl
