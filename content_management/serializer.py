from rest_framework import serializers

from .models import Content_Management, Heading


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
