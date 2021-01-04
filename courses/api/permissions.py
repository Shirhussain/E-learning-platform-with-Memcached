# some times we need to define custom permissions 
# for example here i want to allow only those who enrolled in specific courses
# django alow as to define this methods:
    # has_permission
    # view_label_permission view check 
    # has object permission --> instance permission check 

from rest_framework.permissions import BasePermission

class IsEnrolled(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()
        


