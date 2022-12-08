from django.views.generic import TemplateView


class CorePage(TemplateView):
    template_name = 'core.html'
