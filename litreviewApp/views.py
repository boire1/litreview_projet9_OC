# from django.db import models
from django.contrib.auth.models import User
# from .utils import *
from .utils import (create_user, create_user_view, authenticate_user, logout_user)
from django.contrib.auth.decorators import login_required  # Ajout de l'importation
from django.urls import reverse
from .forms import TicketForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateReviewForm, UpdateReviewForm
from .models import Ticket, Review, UserFollows
from django.contrib.auth import logout
from .forms import CombinedTicketReviewForm
from PIL import Image
import os
from django.conf import settings
from django.contrib import messages
# from django import template
from itertools import chain
# from .models import UserFollows, User
from .forms import ReviewForm
# from litreviewApp.models import Ticket, Review
from django.db.models import Q, Value, CharField, Count, Case, When
from django.http import HttpResponseForbidden
from .forms import UpdateTicketForm

# -------------------------------------Ticket----------------------------------------


@login_required
def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(
            request.POST, request.FILES
        )  # Inclure request.FILES pour traiter l'envoi de fichier
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            return redirect("ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketForm()

    return render(request, "litreviewApp/create_ticket.html", {"form": form})


@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, "litreviewApp/detail_ticket.html", {"ticket": ticket})


@login_required
def update_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        form = UpdateTicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("ticket_detail", ticket_id=ticket.id)
    else:
        form = UpdateTicketForm(instance=ticket)

    return render(
        request, "litreviewApp/update_ticket.html", {"form": form, "ticket": ticket}
    )


@login_required  # Ajout du décorateur
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket.delete()
        return redirect("flux")  # Remplacez 'index' par le nom de vue d'accueil

    return render(request, "litreviewApp/delete_ticket.html", {"ticket": ticket})


# ------------------------------------------Ticket----------------------------------------

# Fonctions pour la classe Review


def index(request):
    return render(request, "litreviewApp/index.html")


# ---------------------------------------------review-------------------------------------------


@login_required
def create_review(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    if request.method == "POST":
        form = CreateReviewForm(
            request.POST, ticket_title=ticket.title, ticket_id=ticket_id
        )
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.created_by = request.user
            review.save()
            return redirect("review_detail", review_id=review.id)
    else:
        form = CreateReviewForm(
            initial={"ticket_id": ticket_id, "rating": 1, "headline": ticket.title},
            ticket_id=ticket_id,
        )

    return render(
        request,
        "litreviewApp/create_review.html",
        {"form": form, "ticket_id": ticket_id},
    )


@login_required
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Vérifier si l'utilisateur connecté est l'auteur de la revue
    if review.created_by != request.user:
        return HttpResponseForbidden(
            "Vous n'avez pas la permission de modifier cette revue."
        )

    if request.method == "POST":
        form = UpdateReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("review_detail", review_id=review.id)
    else:
        form = UpdateReviewForm(instance=review)

    return render(
        request, "litreviewApp/update_review.html", {"form": form, "review": review}
    )


@login_required
def review_detail(request, review_id):
    review = Review.objects.get(id=review_id)
    return render(request, "litreviewApp/review_detail.html", {"review": review})


# ---------------------------------------------review-------------------------------------------


"""afficher la liste des utilisateurs suivis par l'utilisateur connecté """


@login_required
def followers_view(request):
    user = request.user
    followers = UserFollows.objects.filter(followed_user=user).values("created_by")
    follower_users = User.objects.filter(id__in=followers).exclude(id=user.id)
    return render(request, "litreviewApp/followers.html", {"followers": follower_users})


@login_required
def follow_user(request):
    if request.method == "POST":
        follow_username = request.POST.get("follow_username", None)

        if follow_username:
            try:
                followed_user = User.objects.get(username=follow_username)
                if followed_user == request.user:
                    messages.error(
                        request, "Vous ne pouvez pas vous abonner à vous-même."
                    )
                else:
                    # Vérifier si l'utilisateur suit déjà l'utilisateur suivi
                    existing_follow = UserFollows.objects.filter(
                        created_by=request.user, followed_user=followed_user
                    ).exists()
                    if not existing_follow:
                        # Suivre l'utilisateur
                        UserFollows.objects.create(
                            created_by=request.user, followed_user=followed_user
                        )
                        messages.success(
                            request, f"Vous suivez maintenant {follow_username}."
                        )
                    else:
                        messages.warning(
                            request, f"Vous suivez déjà {follow_username}."
                        )
            except User.DoesNotExist:
                messages.error(
                    request, f"L'utilisateur '{follow_username}' n'existe pas."
                )
        else:
            messages.error(request, "Veuillez entrer un nom d'utilisateur valide.")

    # Rediriger l'utilisateur vers la même page après le traitement du formulaire
    return redirect(reverse("abonnement"))


@login_required
def unfollow_user(request):
    if request.method == "POST":
        follow_username = request.POST.get("follow_username")
        try:
            user_to_unfollow = User.objects.get(username=follow_username)
            if request.user != user_to_unfollow:
                UserFollows.objects.filter(
                    created_by=request.user, followed_user=user_to_unfollow
                ).delete()
                return redirect("user_following")
            else:
                error_message = "Vous ne pouvez pas vous désabonner de vous-même."
        except User.DoesNotExist:
            error_message = "Nom d'utilisateur invalide."

        # If there was an error, render the user following page with the error message
        following_users = UserFollows.objects.filter(
            created_by=request.user
        ).select_related("followed_user")
        return render(
            request,
            "litreviewApp/user_following.html",
            {"following_users": following_users, "error_message": error_message},
        )
    else:
        # Redirect to the user following page if the method is not POST
        return redirect("user_following")


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Vérifier si l'utilisateur actuel est l'auteur de la review
    if review.created_by != request.user:
        # Afficher un message d'erreur ou rediriger vers une page d'erreur
        return render(
            request,
            "litreviewApp/error.html",
            {"message": "Vous n'êtes pas autorisé à supprimer cette revue."},
        )

    if request.method == "POST":
        # Supprimer la review
        review.delete()
        # Rediriger vers une page appropriée (par exemple, la page d'accueil)
        return redirect("flux")

    return render(request, "litreviewApp/delete_review.html", {"review": review})


@login_required
def ticket_list_view(request):
    tickets = Ticket.objects.all().order_by("-created_at")

    # Ajouter une propriété user_has_review à chaque ticket
    for ticket in tickets:
        ticket.user_has_review = ticket.review_set.filter(
            created_by=request.user
        ).exists()

    return render(request, "litreviewApp/ticket_list.html", {"tickets": tickets})


@login_required
def create_combined_ticket_review(request):
    if request.method == "POST":
        form = CombinedTicketReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Valider le formulaire
            # ...

            # Enregistrer l'image si elle est fournie
            image = form.cleaned_data["image"]
            image_path = None
            if image:
                ticket_image = Image.open(image)
                ticket_image.thumbnail((50, 50))
                image_path = os.path.join("ticket_images", image.name)
                ticket_image.save(os.path.join(settings.MEDIA_ROOT, image_path))

            # Créer le billet
            ticket = Ticket.objects.create(
                title=form.cleaned_data["ticket_title"],
                description=form.cleaned_data["ticket_description"],
                created_by=request.user,
                image=image_path if image else None,
            )

            # Créer la critique associée au billet
            review = Review.objects.create(
                ticket=ticket,
                rating=form.cleaned_data["review_rating"],
                created_by=request.user,
                headline=form.cleaned_data["review_headline"],
                body=form.cleaned_data["review_body"],
            )

            # Ajouter le nom de l'auteur au contexte
            context = {"form": form, "user": request.user.username}
            return redirect("ticket_detail", ticket_id=ticket.id)

    form = CombinedTicketReviewForm()
    context = {"form": form, "user": request.user.username}
    return render(request, "litreviewApp/create_combined_ticket_review.html", context)


@login_required
def user_following_view(request):
    user = request.user

    # Récupérer les utilisateurs que l'on suit
    following_users = UserFollows.objects.filter(created_by=user).select_related(
        "followed_user"
    )

    # Récupérer les utilisateurs abonnés
    followers = UserFollows.objects.filter(followed_user=user).select_related(
        "created_by"
    )

    # Récupérer les utilisateurs que vous suivez sous forme de liste pour le formulaire "Désabonner"
    following_usernames = [
        following.followed_user.username for following in following_users
    ]

    return render(
        request,
        "litreviewApp/user_following_view.html",
        {
            "following_users": following_users,
            "followers": followers,
            "following_usernames": following_usernames,  # Ajout de la liste des noms d'utilisateurs que vous suivez
        },
    )


@login_required
def abonnement_view(request):
    user = request.user
    
    following_users = UserFollows.objects.filter(created_by=user).select_related(
        "followed_user"
    )
    followers = UserFollows.objects.filter(followed_user=user).select_related(
        "created_by"
    )

    if request.method == "POST":
        # Vérifier si le formulaire de désabonnement est soumis
        if "follow_username" in request.POST:
            follow_username = request.POST["follow_username"]
            try:
                user_to_unfollow = User.objects.get(username=follow_username)
                if user != user_to_unfollow:
                    UserFollows.objects.filter(
                        created_by=user, followed_user=user_to_unfollow
                    ).delete()
                    messages.success(
                        request, f"Vous vous êtes désabonné de {follow_username}."
                    )
                else:
                    messages.error(
                        request, "Vous ne pouvez pas vous désabonner de vous-même."
                    )
            except User.DoesNotExist:
                messages.error(request, "Nom d'utilisateur invalide.")
        else:
            messages.error(request, "Formulaire de désabonnement invalide.")

        # Rediriger l'utilisateur vers la même page après le traitement du formulaire
        return redirect("abonnement")

    return render(
        request,
        "litreviewApp/abonnement.html",
        {
            "following_users": following_users,
            "followers": followers,
        },
    )


@login_required
def user_tickets_view(request):
    user = request.user
    user_tickets = Ticket.objects.filter(created_by=user).order_by("-created_at")

    # Retrieve the reviews associated with each ticket
    for ticket in user_tickets:
        ticket.reviews = Review.objects.filter(ticket=ticket)

    return render(
        request, "litreviewApp/user_tickets.html", {"user_tickets": user_tickets}
    )


@login_required
def search_tickets_view(request):
    if "search_query" in request.GET:
        search_query = request.GET["search_query"]
        tickets = Ticket.objects.filter(title__icontains=search_query).order_by(
            "-created_at"
        )
    else:
        tickets = Ticket.objects.all().order_by("-created_at")

    # Add a user_has_review property to each ticket.
    for ticket in tickets:
        ticket.user_has_review = ticket.review_set.filter(
            created_by=request.user
        ).exists()

    if not tickets:
        messages.info(
            request, "Aucun ticket trouvé pour le terme de recherche spécifié."
        )

    return render(request, "litreviewApp/ticket_list.html", {"tickets": tickets})


@login_required
def flux(request):
    # Get the connected user
    user = request.user

   
    following_users = user.following_users.values("followed_user")
    # Obtain tickets from the logged-in user and from the users to whom the logged-in user is subscribed.
    user_tickets = Ticket.objects.filter(
        Q(created_by=user) | Q(created_by__in=following_users)
    )
    user_tickets = user_tickets.annotate(
        content_type=Value("TICKET", output_field=CharField())
    )

    # Retrieve the reviews made on the tickets of the logged-in user
    user_reviews = Review.objects.filter(
        Q(created_by=user)
        | Q(ticket__created_by__in=user.following_users.values("followed_user"))
        | Q(ticket__in=user_tickets, created_by__isnull=True)
    )
    user_reviews = user_reviews.annotate(
        content_type=Value("REVIEW", output_field=CharField())
    )

    # "Annotate the number of followers for each ticket and review."
    user_tickets = user_tickets.annotate(
        followers_count=Count("followers", distinct=True)
    )
    user_reviews = user_reviews.annotate(
        followers_count=Count("ticket__followers", distinct=True)
    )

    # Use cases and conditions for handling NULL values of followers_count..
    user_tickets = user_tickets.annotate(
        followers_count=Case(
            When(followers_count__isnull=True, then=Value(0)), default="followers_count"
        )
    )
    user_reviews = user_reviews.annotate(
        followers_count=Case(
            When(followers_count__isnull=True, then=Value(0)), default="followers_count"
        )
    )
   

    # Count the number of each data type
    tickets_count = user_tickets.count()
    # following_tickets_count = following_tickets.count()
    reviews_count = user_reviews.count()
    following_reviews_count = Review.objects.filter(
        created_by__in=user.following_users.values("followed_user")
    ).count()
    other_reviews_count = (
        Review.objects.filter(ticket__in=user_tickets).exclude(created_by=user).count()
    )

    # Combine and sort the posts (tickets and reviews)
    posts = sorted(
        chain(user_tickets, user_reviews),
        key=lambda post: post.created_at
        if not post.updated_at
        else max(post.created_at, post.updated_at),
        reverse=True,
    )

    # Pass all the necessary data within the context."
    return render(
        request,
        "litreviewApp/flux.html",
        context={
            "posts": posts,
            "tickets_count": tickets_count,
            
            "reviews_count": reviews_count,
            "following_reviews_count": following_reviews_count,
            "other_reviews_count": other_reviews_count,
        },
    )


@login_required
def create_reviewstand(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.created_by = request.user
            review.save()
            return redirect("flux")
    else:
        form = ReviewForm()

    return render(request, "litreviewApp/create_reviewstand.html", {"form": form})


def logout_view(request):
    logout(request)
    return render(request, "litreviewApp/logout.html")
