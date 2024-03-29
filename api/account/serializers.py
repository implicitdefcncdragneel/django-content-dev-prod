import logging
from django.utils.encoding import smart_str
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Profile
User = get_user_model()
logger = logging.getLogger(__name__)

class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {'password' : {'write_only': True},}

    def create(self, validated_data):
        member = User.objects.create(username=validated_data['username'],
                email=validated_data['email'],
                first_name = validated_data['first_name'],
                last_name = validated_data['last_name']
                )
        member.set_password(validated_data['password'])
        member.save()
        return member

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=8,required=True)
    class Meta:
        model = User
        fields = ['email',]

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=18, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)
    
    class Meta:
        fields = ['password', 'uidb64']

    def validate(self, attrs):
        password = attrs.get('password')
        uidb64 = attrs.get('uidb64')
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            user.set_password(password)
            user.save()
            return (user)
        except User.DoesNotExist as e:
            logger.error(str(e))
            raise serializers.ValidationError(detail="User Does Not Exits")
        except Exception as e :
            logger.error(str(e))
            raise e 

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": {"message":"Bad Request","errors":"No active account found with the given credentials"}
    }
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data
class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")
    profile_photo = serializers.ReadOnlyField(source="profile.profile_photo")
    country = CountryField(source="profile.country")
    city = serializers.CharField(source="profile.city")
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "phone_number",
            "profile_photo",
            "country",
            "city",
        ]

    def get_first_name(self, obj):
        return obj.first_name.title()

    def get_last_name(self, obj):
        return obj.last_name.title()

    def get_full_name(self, obj):
        first_name = obj.user.first_name.title()
        last_name = obj.user.last_name.title()
        return f"{first_name} {last_name}"

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if instance.is_superuser:
            representation["admin"] = True
        return representation

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    full_name = serializers.SerializerMethodField(read_only=True)
    profile_photo = serializers.SerializerMethodField()
    country = CountryField(name_only=True)
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "id",
            "profile_photo",
            "phone_number",
            "about_me",
            "gender",
            "country",
            "city",
            "twitter_handle",
            "facebook_handle",
            "instagram_handle",
            "following",
        ]

    def get_full_name(self, obj):
        first_name = obj.user.first_name.title()
        last_name = obj.user.last_name.title()
        return f"{first_name} {last_name}"

    def get_profile_photo(self, obj):
        try:
            return obj.profile_photo.url
        except Exception as e:
            return None

    def get_following(self, instance):
        request = self.context.get("request", None)
        if request is None:
            return None
        if request.user.is_anonymous:
            return False

        current_user_profile = request.user.profile
        followee = instance
        following_status = current_user_profile.check_following(followee)
        return following_status


class UpdateProfileSerializer(serializers.ModelSerializer):
    country = CountryField(name_only=True)
    phone_number=PhoneNumberField(required=False)

    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "profile_photo",
            "about_me",
            "gender",
            "country",
            "city",
            "twitter_handle",
            "facebook_handle",
            "instagram_handle"
            ]


class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    following = serializers.BooleanField(default=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "first_name",
            "last_name",
            "profile_photo",
            "about_me",
            "twitter_handle",
            "facebook_handle",
            "instagram_handle",
            "following",
        ]

