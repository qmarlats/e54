from django import template

register = template.Library()


@register.inclusion_tag("core/form_errors.html")
def show_form_errors(form):
    return {
        "form": form,
    }
