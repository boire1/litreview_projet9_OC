from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect

# from django.http import HttpResponse
from .forms import CreateUserForm
from django.contrib import messages


def create_user(username, password, confirm_password):
    if password == confirm_password:
        try:
            user = User.objects.create_user(username=username, password=password)
            return user
        except ValueError:
            raise ValueError("Nom d'utilisateur déjà pris")
    else:
        raise ValueError("Les mots de passe ne correspondent pas")


def create_user_view(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            try:
                user = create_user(username, password, confirm_password)
                if user is not None:
                    messages.success(
                        request,
                        "Vous êtes inscrit avec succès. Veuillez vous connecter maintenant.",
                    )
                    # Utilisateur créé avec succès
                    return redirect("login")
            except ValueError as e:
                error_message = str(e)
                return render(
                    request,
                    "litreviewAPP/create_user.html",
                    {"form": form, "error_message": error_message},
                )
    else:
        form = CreateUserForm()

    return render(request, "litreviewAPP/create_user.html", {"form": form})


def authenticate_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            # L'utilisateur est authentifié avec succès
            login(request, user)
            return redirect("flux")
        else:
            # L'authentification a échoué
            error_message = "Nom d'utilisateur ou mot de passe incorrect"
            return render(
                request, "litreviewAPP/login.html", {"error_message": error_message}
            )
    else:
        return render(request, "litreviewAPP/login.html")


# def user_profile_login_view(request):
#     if request.user.is_authenticated:
#         username = request.user.username
#         return render(request, "litreviewAPP/user_profile.html", {"username": username})
#     else:
#         return redirect("login")


def logout_user(request):
    logout(request)
    return render(request, "litreviewApp/logout.html")
