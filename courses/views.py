from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
# to know more about django-braces you have check this out https://django-braces.readthedocs.io/
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from . models import Course
from . forms import ModuleFormSet



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


# for more info take a look at:
# https://ccbv.co.uk/projects/Django/3.0/django.views.generic.base/TemplateResponseMixin/
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None 

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 
                                        'formset': formset
        })

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('courses:manage_course_list')
        return self.render_to_response({'course':self.course, 'formset': formset})
