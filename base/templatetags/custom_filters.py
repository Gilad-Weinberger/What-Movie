from django import template

register = template.Library()

@register.filter(name='get_first_name')
def get_first_name(full_name):
    return full_name.split()[0] if full_name else ''