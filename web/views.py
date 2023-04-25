from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from telebot.apihelper import ApiTelegramException

from bot import keyboards as kb
from bot.config import Config
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
        bot.send_message(req.student.telegram_id, Config.dialog_finished, reply_markup=kb.start_keyboard())
        req.student.state = "start"
        req.student.save()
    return HttpResponse("")


@auth_required
def requests_table(request):
    if request.user.is_superuser:
        filter_requests = Request.objects.all()
    else:
        filter_requests = Request.objects.filter(destination=request.user.username)
    return render(request, 'requests_table.html', {
        "requests": filter_requests.order_by("status", "-id")
    })


@auth_required
def index(request):
    return render(request, 'index.html')


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
