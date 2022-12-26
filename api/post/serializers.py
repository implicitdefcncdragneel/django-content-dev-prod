from rest_framework import serializers
from api.post.models import Post
from api.account.models import User
from api.post.field_utils import TagRelatedField

class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),default=serializers.CurrentUserDefault(),required=False)
    tags = TagRelatedField(many=True,required=False)
    post_image = serializers.ImageField()

    class Meta:
        model = Post
        exclude = ["updated_at","pkid"]