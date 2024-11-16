from django import template
register = template.Library()

@register.filter
def fieldtype(field):
    return field.field.widget.__class__.__name__.lower()