from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import Post
from .models import Comment
from django.contrib.auth import get_user_model


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class UserEditForm(UserChangeForm):
    password = None
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')