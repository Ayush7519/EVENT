from django.utils.crypto import get_random_string
from rest_framework import serializers

from .models import Blog, Content_Management, Heading


# Content_management
# creating the serializer for the content_management.
class Content_ManagementSerializer(serializers.ModelSerializer):
    # heading = serializers.StringRelatedField()

    class Meta:
        model = Content_Management
        fields = "__all__"


class Content_ManagementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content_Management
        fields = "__all__"
        depth = 1


# Heading
# #creating the serializer for the heading.
class HeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heading
        fields = "__all__"


# trying some thing new
class ImageUploaderSerializer(serializers.Serializer):
    file = serializers.ImageField()

    def validate(self, attrs):
        image_name = attrs.get("file")
        name = self.context.get("user")
        ext = image_name.name.split(".")[-1]
        print(ext)
        valide_extension = ["jpg", "jpeg", "png"]
        if ext.lower() not in valide_extension:
            raise serializers.ValidationError(
                "Extension does not match. It should be of png, jpg, jpeg"
            )
        else:
            new_filename = f"{name}_{get_random_string(length=3)}.{ext}"
            attrs["file"].name = new_filename
            return attrs


# For the blog
# serializer for the blog create.
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"
