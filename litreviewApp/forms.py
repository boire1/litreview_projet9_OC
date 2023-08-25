from django import forms
from .models import Ticket
from .models import Review
from django.core.validators import MinValueValidator, MaxValueValidator


class CreateUserForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=100)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label="Confirmez le mot de passe", widget=forms.PasswordInput
    )


class CreateReviewForm(forms.ModelForm):
    ticket_id = forms.IntegerField(
        widget=forms.TextInput(attrs={"readonly": True}), required=False
    )

    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]

    def __init__(self, *args, **kwargs):
        ticket_title = kwargs.pop("ticket_title", "")
        ticket_id = kwargs.pop("ticket_id", "")
        super().__init__(*args, **kwargs)
        self.fields["headline"].widget = forms.TextInput(
            attrs={"value": ticket_title, "readonly": True}
        )
        self.fields["ticket_id"].initial = ticket_id


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]  #


class UpdateReviewForm(forms.ModelForm):
    created_by_name = forms.CharField(label="Auteur", disabled=True)

    class Meta:
        model = Review
        fields = ["rating", "headline", "body"]

        widgets = {
            "created_by_name": forms.TextInput(),
            "created_by": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["created_by_name"].initial = self.instance.created_by.username


class CombinedTicketReviewForm(forms.Form):
    ticket_title = forms.CharField(max_length=128, label="Titre du billet")
    ticket_description = forms.CharField(
        widget=forms.Textarea, label="Description du billet"
    )
    review_rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], label="Évaluation"
    )
    review_headline = forms.CharField(max_length=128, label="Titre de la critique")
    review_body = forms.CharField(widget=forms.Textarea, label="Corps de la critique")
    image = forms.ImageField(label="Image du billet", required=False)
    author = forms.CharField(widget=forms.HiddenInput(), required=False)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "headline", "body"]


class UpdateTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
