from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect

from client.views import common_login, common_signup
from .forms import PartnerForm, MenuForm
from .models import Menu


URL_LOGIN = '/partner/login/'

def partner_group_check(user):
    return "partner" in user.groups.all()

# Create your views here.
def index(request):
    ctx = {}
    if request.method == "GET":
        partner_form = PartnerForm()
        ctx.update({"form" : partner_form})
    elif request.method == "POST":
        partner_form = PartnerForm(request.POST)
        if partner_form.is_valid():
            partner = partner_form.save(commit=False)
            partner.user = request.user
            partner.save()
            return redirect("/partner/")
        else:
            ctx.update({"form" : partner_form})

    return render(request, "index.html", ctx)

def login(request):
    ctx = {}
    return common_login(request, ctx, "partner")

def signup(request):
    ctx = {}
    return common_signup(request, ctx, "partner")

def logout(request):
    auth_logout(request)
    return redirect("/partner/")

@login_required(login_url=URL_LOGIN)
def edit_info(request):
    ctx = {}
    # Article.objects.all() # qurey
    # partner = Partner.objects.get(user=request.user)
    if request.method == "GET":
        partner_form = PartnerForm(instance=request.user.partner)
        ctx.update({"form" : partner_form})
    elif request.method == "POST":
        partner_form = PartnerForm(
            request.POST,
            instance=request.user.partner,
        )
        if partner_form.is_valid():
            partner = partner_form.save(commit=False)
            partner.user = request.user
            partner.save()
            return redirect("/partner/")
        else:
            ctx.update({"form" : partner_form})

    return render(request, "edit_info.html", ctx)

@login_required(login_url=URL_LOGIN)
def menu(request):
    ctx = {}
    # if request.user.is_anonymous or request.user.partner is None:
    #     return redirect("/partner/")
    menu_list = Menu.objects.filter(partner = request.user.partner)
    ctx.update({"menu_list": menu_list})

    return render(request, "menu_list.html", ctx)

@login_required(login_url=URL_LOGIN)
@user_passes_test(partner_group_check, login_url=URL_LOGIN)
def menu_add(request):
    ctx = {}
    # if "partner" not in request.user.groups.all():
    #     return redirect("/")

    if request.method == "GET":
        form = MenuForm()
        ctx.update({ "form": form })
    elif request.method == "POST":
        form = MenuForm(request.POST, request.FILES)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.partner = request.user.partner
            menu.save()
            return redirect("/partner/menu/")
        else:
            ctx.update({ "form": form })

    return render(request, "menu_add.html", ctx)

@login_required(login_url=URL_LOGIN)
def menu_detail(request, menu_id):
    menu = Menu.objects.get(id=menu_id)
    ctx = { "menu" : menu }
    return render(request, "menu_detail.html", ctx)

@login_required(login_url=URL_LOGIN)
def menu_edit(request, menu_id):
    ctx = { "replacement" : "수정" }
    menu = Menu.objects.get(id=menu_id)
    if request.method == "GET":
        form = MenuForm(instance=menu)
        ctx.update({ "form": form })
    elif request.method == "POST":
        form = MenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.partner = request.user.partner
            menu.save()
            return redirect("/partner/menu/")
        else:
            ctx.update({ "form": form })

    return render(request, "menu_add.html", ctx)

@login_required(login_url=URL_LOGIN)
def menu_delete(request, menu_id):
    menu = Menu.objects.get(id=menu_id)
    menu.delete()
    return redirect("/partner/menu/")
