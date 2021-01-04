# viewsets alow you to define the intraction of your api and let rest framework build dynamically
# with router object. by using viewset you are avoiding repeating logic or multiple view
from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action 

from ..models import Subject, Course
from .permissions import IsEnrolled
from .serializers import SubjectSerializer,\
    SubjectSerializer, CourseSerializer,\
    CourseWithContentsSerializer

# some of the build in permession system in rest framework are:
    # allow any --> un restricted access regardless if the user is authenticated or not
    # is_authenticated --> access to authenticated only
    # is_authenticated_or_readonly ---> authenticated user has access but other just read only per
    # django model permissions:
        # permission tied to django.contrib.auth --> the view require queryset attribute
        # only authenticated user with model signed or granted permission 
    # django object permission:
        # django permission per object 
        # if users are dinied permissins the will get an http error code 
    

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # the decorator allow as to write custom attribute to the action
    @action(
        detail=True,
        methods = ['post'],
        authentication_classes=[BasicAuthentication],
        permission_classes = [IsAuthenticated]
    )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    @action(
        detail=True,
        methods=['get'],
        serializer_class = CourseWithContentsSerializer,
        authentication_classes = [BasicAuthentication],
        permission_classes = [IsAuthenticated, IsEnrolled]
    )
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# building Custom:
    # provides APIView class: build API functionality on top of django's view class
    # APIView differs from view in using REST Framework's methods 
    # also it has build-in authentication and authorization
# class CourseEnrollView(APIView):
#     authentication_classes = (BasicAuthentication,)
#     permission_classes = (IsAuthenticated,)


#     def post(self, request, pk, format=None):
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})