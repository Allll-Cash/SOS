from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from telebot.apihelper import ApiTelegramException

from bot import keyboards as kb
from bot.config import Config, FACULTIES, OTHER_PROBLEMS, STUDSOVETS
from bot.management.commands.bot import bot
from bot.models import Request, TelegramMessage
from common.utils import auth_required
from studreply.integrations import minio


def auth(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponseRedirect('/auth?err=true')
        login(request, user)
        return HttpResponseRedirect("/")
    return render(request, "auth.html", {"error": "err" in request.GET})


@auth_required
def photo(request):
    if 'filename' in request.GET:
        with open(f'content/{request.GET["filename"]}', 'rb') as fp:
            return HttpResponse(
                fp.read(), content_type="image/png"
            )
    return HttpResponse(
        minio.get_object(f"photos/{request.GET['id']}.jpg"), content_type="image/jpg"
    )


@auth_required
def send_message(request):
    req = Request.objects.get(id=request.GET['request_id'])
    if req.destination != request.user.username and not request.user.is_superuser:
        return HttpResponse("")
    if req.status == 2:
        return HttpResponse("")
    try:
        bot.send_message(req.student.telegram_id, text=request.GET['message'], reply_markup=kb.finish_dialog_keyboard())
        TelegramMessage.objects.create(request=req, sent_by_operator=True, text=request.GET['message'])
    except ApiTelegramException as ate:
        if ate.error_code == 403:
            TelegramMessage.objects.create(request=req, sent_by_operator=True, text="Не удалось отправить сообщение, так как пользователь заблокировал бота, сейчас автоматически произойдет сброс сессии")
            req.student.state = "start"
            req.student.save()
            req.status = 2
            req.save()
    return HttpResponse("")


@auth_required
def set_status(request):
    req = Request.objects.get(id=request.GET['request_id'])
    if req.destination != request.user.username and not request.user.is_superuser:
        return HttpResponse("")
    req.status = int(request.GET['status'])
    req.save()
    if req.status == 2:
        try:
            bot.send_message(req.student.telegram_id, Config.dialog_finished, reply_markup=kb.start_keyboard())
        except Exception as e:
            pass
        req.student.state = "start"
        req.student.save()
        TelegramMessage.objects.create(request=req, text=Config.operator_finished, sent_by_operator=True)
    return HttpResponse("")


@auth_required
def requests_table(request):
    reasons = request.GET['reasons'].split('_')
    reasons_list = [key for key, value in OTHER_PROBLEMS.items() if value in reasons]
    filter_requests = Request.objects.filter(ready=True, reason__in=reasons_list)
    if not request.user.is_superuser:
        filter_requests = filter_requests.filter(destination=request.user.username)
    return render(request, 'requests_table.html', {
        "requests": filter_requests.order_by("status", "-id")
    })


@auth_required
def index(request):
    role = 'admin'
    need_filter = True
    for key, value in FACULTIES.items():
        if value == request.user.username:
            role = key
            break
    role = STUDSOVETS.get(request.user.username) or role
    return render(request, 'index.html', {
        'role': role,
        'need_filter': need_filter
    })


@auth_required
def some_request(request):
    request_id = int(request.GET['id'])
    if request_id == 0:
        return HttpResponse("")
    req = Request.objects.get(id=request.GET['id'])
    if req.destination != request.user.username and not request.user.is_superuser:
        return HttpResponse("")
    return render(request, 'some_request.html', {"request": req})


@auth_required
def exit_account(request):
    logout(request)
    return HttpResponseRedirect("/auth")


@auth_required
def can_write(request):
    request_id = int(request.GET['request_id'])
    if request_id == 0:
        return JsonResponse({"can_write": False})
    req = Request.objects.get(id=request_id)
    return JsonResponse({"can_write": req.status == 0})
