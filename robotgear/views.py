from django.views.generic.base import TemplateView


class TermsAndConditions(TemplateView):
    template_name = "terms_and_conditions.html"


class IndexView(TemplateView):
    template_name = "index.html"

