from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter."""
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None
