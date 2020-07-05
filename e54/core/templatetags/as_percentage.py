from django import template

register = template.Library()


@register.filter
def as_percentage(value):
    return f"{value*100}"
