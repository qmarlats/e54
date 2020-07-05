from django import template
from django.urls import reverse_lazy

register = template.Library()


@register.inclusion_tag("core/bulk_delete_modal.html")
def show_bulk_delete_modal(records_count, url, year=None, month=None, day=None):
    if day:
        modal_id = day.strftime("%Y-%m-%d")
        date = day.strftime("%x")
        url = reverse_lazy(
            url,
            kwargs={
                "year": day.strftime("%Y"),
                "month": day.strftime("%m"),
                "day": day.strftime("%d"),
            },
        )
    elif month:
        modal_id = month.strftime("%Y-%m")
        date = month.strftime("%B (%Y)")
        url = reverse_lazy(
            url, kwargs={"year": month.strftime("%Y"), "month": month.strftime("%m")}
        )
    elif year:
        modal_id = year.strftime("%Y")
        date = year.strftime("%Y")
        url = reverse_lazy(url, kwargs={"year": year.strftime("%Y")})
    return {
        "records_count": records_count,
        "modal_id": modal_id,
        "date": date,
        "url": url,
    }
