from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField


class Subject(models.Model):
    """Model definition for Subject."""

    title = models.CharField(_("title"), max_length=200)
    slug  = models.SlugField(_("slug"), unique=True, max_length=210)

    class Meta:
        """Meta definition for Subject."""

        ordering = ('title', )
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        """Unicode representation of Subject."""
        return self.title


class Course(models.Model):
    """Model definition for Course."""

    owner = models.ForeignKey(User, verbose_name=_("Owner"), related_name="courses_created", on_delete=models.CASCADE)
    subject = models.ForeignKey("courses.Subject", verbose_name=_("Subject"), related_name="courses", on_delete=models.CASCADE)
    title   = models.CharField(_("Title"), max_length=200)
    slug    = models.SlugField(_("Slug"), max_length=210)
    overview = models.TextField(_("Overview"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    students = models.ManyToManyField(User, verbose_name=_("Students"), related_name="courses_joined", blank=True)
    
    class Meta:
        """Meta definition for Course."""

        ordering = ('created', )
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        """Unicode representation of Course."""
        return str(self.subject)


class Module(models.Model):
    """Model definition for Module."""

    course = models.ForeignKey(Course, verbose_name=_("Course"), related_name="modules", on_delete=models.CASCADE)
    title   = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"))
    order = OrderField(blank=True, for_fields=['course'])


    class Meta:
        """Meta definition for Module."""
        
        ordering = ['order']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self):
        """Unicode representation of Module."""
        return f'{self.order}, {self.title}'


class Content(models.Model):
    """Model definition for Content.
    - the content type and object_id field have column in database table 
    - The item field alow you to set the related object directly 
    - use different model for each type of content
    """
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    order = OrderField(blank=True, for_fields=['module'])
    content_type = models.ForeignKey(ContentType, verbose_name=_("Content type"),
                                    # model__in lookup is going to filter the query to the content obj
                                    # with the model attribute which is 'text', 'video', 'image' and 'file'
                                    limit_choices_to={'model__in': ('text', 'video', 'image', 'file')},
                                    on_delete=models.CASCADE
    )
    # object_id is for storing the primary key of the related object
    object_id = models.PositiveIntegerField(_("Object Id"))
    item = GenericForeignKey('content_type', 'object_id')

    # to understand better the content type and generic relation you have to see this link
    # https://stackoverflow.com/questions/20895429/how-exactly-do-django-content-types-work


    class Meta:
        """Meta definition for Content."""

        ordering = ['order']
        verbose_name = 'Content'
        verbose_name_plural = 'Contents'


class ItemBase(models.Model):
    """Model definition for ItemBase."""

    owner = models.ForeignKey(User, verbose_name=_("Owner"), related_name='%(class)s_related',
                                on_delete=models.CASCADE
    )
    title = models.CharField(_("Title"), max_length=255)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    class Meta:
        """Meta definition for ItemBase."""
        
        abstract = True
        verbose_name = 'ItemBase'
        verbose_name_plural = 'ItemBases'

    def __str__(self):
        """Unicode representation of ItemBase."""
        return self.title


class Text(ItemBase):
    # that related name with %(class)s which i created is very crucial which means that 
    # now for every child class it's just takes it's child class name ass well i.g
    # here the related name would be texts
    content = models.TextField(_("Text"),)


class File(ItemBase):
    file = models.FileField(_("File"), upload_to='Uploads/courses/files', max_length=100)


class Video(ItemBase):
    url = models.URLField(_("URL"), max_length=200)


class Image(ItemBase):
    file = models.FileField(_("File"), upload_to='Uploads/courses/Images', max_length=100)