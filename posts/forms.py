from django import forms


class PostForm(forms.Form):
    title = forms.CharField(max_length=100)
    desc = forms.CharField(widget=forms.Textarea)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    location = forms.CharField(widget=forms.HiddenInput)  # render manually
