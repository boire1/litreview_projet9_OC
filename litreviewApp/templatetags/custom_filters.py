# custom_filters.py
from django import template

register = template.Library()


@register.filter
def generate_star_rating(value):
    try:
        rating = int(value)
        if rating < 1:
            raise ValueError("Rating value should be between 1 and 5.")
    except (ValueError, TypeError):
        return ""  # Or return any other default message or an empty string

    full_stars = "★" * rating
    empty_stars = "☆" * (5 - rating)
    return f"{full_stars}{empty_stars}"
