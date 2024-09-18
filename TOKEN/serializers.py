from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = '__all__'

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Borrow
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']

    def create(self, validated_data):
        user = User(username = validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username',instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
