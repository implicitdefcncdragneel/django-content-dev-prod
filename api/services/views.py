from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from api.post.models import Post
from api.services.models import Rating
from api.utils.response_schema import response_schema
from api.utils.custom_view_exceptions import AlreadyRated, CantRateYourPost

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_rating_view(request, id):
    author = request.user
    post = Post.objects.get(id=id)
    data = request.data
    if post.author == author:
        raise CantRateYourPost
    already_exists = post.post_ratings.filter(rated_by__pkid=author.pkid).exists()
    if already_exists:
        raise AlreadyRated
    elif data["value"] == 0:
        return Response(response_schema("Bad Request","You can't give a zero rating"), status=status.HTTP_400_BAD_REQUEST)
    else:
        rating = Rating.objects.create(post=post,rated_by=request.user,value=data["value"],review=data["review"])
        rating.save()
        return Response(response_schema("Rating has been added"), status=status.HTTP_201_CREATED)