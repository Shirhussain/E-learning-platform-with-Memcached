from django import forms
from courses.models import Course

class CourseEnrollForm(forms.Form):
    # her i use hidden input wedgit, because i don't wanna show this one to the user
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput)
    