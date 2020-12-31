from django.shortcuts import render
from django.views.generic.list import ListView, CreateView, UpdateView, DeleteView, EditView
from django.urls import reverse_lazy

from . models import Course


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'


class OwnerMixin(object):
    def get_queryset(self):
        qs =  super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user 
        # form_valid is executed when the submitted form is valid 
        # the default behavior is saving instance and redirecting the user to success_url 
        # i have overwrite this method  and set the current user automatically when object bing saved 
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin):
    model = Course


class OwnerCourseEditMixin(OwnerCourseEditMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/from.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(OwnerCourseMixin, CreateView):
    pass 


class CourseUpdateView(OwnerCourseMixin, UpdateView):
    pass 


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/list.html'


