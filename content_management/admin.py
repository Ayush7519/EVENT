from django.contrib import admin

from .models import Blog, Comment, Content_Management, Heading


# admin registration for the heading.
class Heading_Admin(admin.ModelAdmin):
    list_display = [
        "id",
        "heading",
    ]


admin.site.register(Heading, Heading_Admin)


# admin registrstion of the contant_management.
class Content_ManagementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "heading",
        "content",
        "date_created",
        "date_updated",
        "updated_by",
        "status",
    )


admin.site.register(Content_Management, Content_ManagementAdmin)


# creating the admin pannel for the blog.
class Blog_Admin(admin.ModelAdmin):
    list_display = (
        "id",
        "content",
        "date_created",
        "date_updated",
        "created_by",
        "updated_by",
    )


admin.site.register(Blog, Blog_Admin)


# regstring the comment.
class Comment_Admin(admin.ModelAdmin):
    list_display = (
        "id",
        "blog",
        "content",
        "data_created",
        "data_updated",
        "like",
    )


admin.site.register(Comment, Comment_Admin)
