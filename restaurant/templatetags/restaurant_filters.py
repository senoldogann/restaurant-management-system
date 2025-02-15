from django import template

register = template.Library()

@register.filter
def filter_rating(reviews, rating):
    """Belirli bir puana sahip değerlendirmelerin sayısını döndürür."""
    return len([review for review in reviews if review.rating == int(rating)]) 