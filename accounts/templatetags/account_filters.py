from django import template

register = template.Library()

@register.filter
def getattr_filter(obj, attr):
    """Gets an attribute of an object dynamically from a string name"""
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return '' 