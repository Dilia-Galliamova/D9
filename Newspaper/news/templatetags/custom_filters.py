from django import template


register = template.Library()


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter()
def censor(txt):
   for s in txt:
      if s.isupper():
         txt = txt.replace(s, '*')

   return txt
