from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormView
from posts.forms import PostForm


def post_detail(slug):
    pass


class PostFormView(FormView):
    form_class = PostForm
    template_name = 'add_post.html'

    def get_success_url(self):
        pass

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('images')
        if form.is_valid():
            for f in files:
                pass
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
