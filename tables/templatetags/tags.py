from django import template
import re

register = template.Library()
@register.simple_tag
def active(request, pattern):
    stringPattern = '^' + pattern + '$'
    if re.search(stringPattern, request.path):
        return 'nav-item active'
    return 'nav-item'