from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

def update_attrs(widget, attrs):
    """Helper function to update widget attributes."""
    existing = widget.attrs.copy() if hasattr(widget, 'attrs') else {}
    existing.update(attrs)
    return existing

@register.filter
def add_class(field, css_class):
    """Add a CSS class to the field."""
    if hasattr(field, 'as_widget'):
        attrs = update_attrs(field.field.widget, {})
        if 'class' in attrs:
            attrs['class'] = f"{attrs['class']} {css_class}"
        else:
            attrs['class'] = css_class
        return field.as_widget(attrs=attrs)
    return field

@register.filter
def add_attr(field, attr_string):
    """Add an attribute to the field."""
    if not attr_string or not hasattr(field, 'as_widget'):
        return field
        
    attr_name, attr_value = attr_string.split(':', 1)
    attrs = update_attrs(field.field.widget, {attr_name: attr_value})
    return field.as_widget(attrs=attrs)

@register.filter
def placeholder(field, text):
    """Add placeholder text to the field."""
    if not hasattr(field, 'as_widget'):
        return field
    attrs = update_attrs(field.field.widget, {'placeholder': text})
    return field.as_widget(attrs=attrs)

@register.filter
def with_attrs(field, attrs_dict):
    """Add multiple attributes to the field."""
    if not hasattr(field, 'as_widget'):
        return field
    attrs = update_attrs(field.field.widget, attrs_dict)
    return field.as_widget(attrs=attrs) 