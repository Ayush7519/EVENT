from django.db import models

from ems.validations import isalphavalidator


class Heading(models.Model):
    heading = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading


class Content_Management(models.Model):
    STATUS_CHOICES = (
        ("Draft", "draft"),
        ("Publish", "publish"),
    )
    heading = models.ForeignKey(
        Heading,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    content = models.TextField(null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=10)
    status = models.CharField(choices=STATUS_CHOICES, max_length=100)

    def __str__(self):
        return self.heading.heading


# model for the blog.
class Blog(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title


# model for the comment for the blog.
class Comment(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    content = models.TextField(blank=False, null=False)
    data_created = models.DateTimeField(auto_now_add=True)
    data_updated = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)

    def __str__(self):
        return self.content
