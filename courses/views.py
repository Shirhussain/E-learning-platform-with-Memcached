from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# to know more about django-braces you have check this out https://django-braces.readthedocs.io/
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
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


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'


# you need to go in '/admin' and create a group for example by the name of 'Instaractor' 
# then give some permissions like aded course and ...
class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course' 


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    success_url = reverse_lazy('courses:manage_course_list')
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'
    # template_name = 'courses/manage/module/formset.html'


class CourseModuleUpdateView(UpdateView):
    pass 


