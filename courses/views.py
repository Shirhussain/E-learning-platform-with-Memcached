from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
# to know more about django-braces you have check this out https://django-braces.readthedocs.io/
from braces.views import LoginRequiredMixin, PermissionRequiredMixin, CsrfExemptMixin, JsonRequestResponseMixin
from django.urls import reverse_lazy
from django.forms.models import modelform_factory
from django.apps import apps

from . models import Course, Module, Content
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


# it will alow as to create and update diffrent models
# https://ccbv.co.uk/projects/Django/3.0/django.views.generic.base/TemplateResponseMixin/
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None 
    model = None 
    obj = None 
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        # here we check if the given model is one of the four content model 
        if model_name in ['text', 'image', 'video', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    
    def get_form(self, model, *args, **kwargs):
        # i build a dynamic form with form_factory 
        # since i specified model only for 'image', 'file', 'video' and 'text' 
        # so i use exclude parameter to specify common field to exclude from the field
        Form = modelform_factory(
            model,
            exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)

    # dispatch receive the url parametter to store the corresponding module 
    # module_id = the id for the module of the content which associated with 
    # model_name = the model name for create/update
    # id = the id of teh object which going to be update or create 
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(
                                        Module,
                                        id=module_id,
                                        course__owner=request.user
                                        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(
                                        self.model,
                                        id=id,
                                        owner = request.user 
                                        )
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)
        
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj) 
        return self.render_to_response({
                                        'form': form,
                                        'object': self.obj
                                        })
    
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
                            self.model, 
                            instance=self.obj, 
                            data = request.POST, 
                            files = request.FILES
                            )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user 
            obj.save()
            if not id:
                # new Content 
                # if id doesn't exist we know that user is going to create a new obj 
                Content.objects.create(
                                        module = self.module,
                                        item = obj 
                )
            return redirect('courses:module_content_list', self.module.id)
        return self.render_to_response({
                                        'form': form, 
                                        'object': self.obj
                                        })


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(
                                    Content,
                                    id=id,
                                    module__course__owner=request.user 
                                    )
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('courses:module_content_list', module.id)
    
    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(
                                    Module,
                                    id=module_id,
                                    course__owner=request.user)
        return self.render_to_response({'module': module})


# CsrfExemptMixin is to avoid checking for a csrf token in post request
# we need this to perform ajax post request without generating csrf_token 
# JsonRequestResponseMixin: passes request data as json and also serialize the response json 
# and return HttpResponse with the application /json content type 
class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(
                                id=id,
                                course__owner=request.user
                                ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id,
                module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})
