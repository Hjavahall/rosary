from django import template
register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except IndexError:
        return None

@register.filter    
def make_range(value):
    return range(value)
