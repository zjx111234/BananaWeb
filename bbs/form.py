from django.forms import ModelForm
from django import forms
from bbs import models
from django.contrib.auth.models import User


# from django.contrib.auth.forms.UserCreationForm


class ArticleModelForm(ModelForm):
    class Meta:
        model = models.Article
        exclude = ('author', 'pub_date', 'priority', 'thumb_count', 'disgusting_count', 'click_count')

    def __init__(self, *args, **kwargs):
        super(ArticleModelForm, self).__init__(*args, **kwargs)
        category_choice = [
            (3, '校园'),
            (4, '亚洲'),
            (5, '欧美'),
            (6, 'TokyoHot'),
        ]
        self.fields['title'].widget.attrs['placeholder'] = '请输入标题'
        self.fields['brief'].widget.attrs['placeholder'] = '请输入文章简介'
        self.fields['category'].widget.choices = category_choice
        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            class_name = 'publish-' + field_name
            field.widget.attrs.update({'class': class_name})


class ShortArticleModelForm(ModelForm):
    class Meta:
        model = models.ShortArticles
        exclude = ('author', 'pub_date', 'priority', 'thumb_count', 'disgusting_count')
    def __init__(self, *args, **kwargs):
        super(ShortArticleModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = '请输入标题'
        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            class_name = 'publish-' + field_name
            field.widget.attrs.update({'class': class_name})


class ChangePwdForm(forms.Form):
    uid = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'class': 'control-input'
            }
        ),
    )
    new_password1 = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'class': 'control-input'
            }
        ),
    )
    new_password2 = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'class': 'control-input'
            }
        ),
    )

    def clean(self):
        from django.contrib.auth import authenticate
        if self.is_valid():
            uid = self.cleaned_data.get('uid')
            username = User.objects.get(id=uid)
            old_password = self.cleaned_data.get('old_password')
            user = authenticate(username=username, password=old_password)
            if user is None or not user.is_active:
                raise forms.ValidationError(u"原密码错误")
            if self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
                raise forms.ValidationError(u"两次输入的新密码不一样")
        else:
            raise forms.ValidationError(u"所有项都为必填项")
        cleaned_data = super(ChangePwdForm, self).clean()
        return cleaned_data


class UserProfileModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileModelForm, self).__init__(*args, **kwargs)
        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            field.widget.attrs.update({'class': 'control-input'})
        self.base_fields['birth'].error_messages = {'invalid': '日期格式错误'}

    class Meta:
        model = models.UserProfile
        exclude = (
            'user', 'user_level', 'experience', 'user_level', 'article_like', 'friends', 'sign_up_time', 'head_img')


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100, widget=forms.TextInput(attrs={'class': 'register-name'}),
                               error_messages={'required': '用户名不能为空', 'invalid': '用户名格式错误'})
    nickname = forms.CharField(label='昵称', widget=forms.TextInput(attrs={'class': 'register-nickname'}),
                               error_messages={'required': '昵称不能为空', 'invalid': '昵称格式错误'})
    email = forms.EmailField(label='邮箱')
    head_img = forms.ImageField(label='头像', widget=forms.FileInput(attrs={'class': 'register-img'}),
                                error_messages={'required': '请上传头像', 'invalid': '头像格式错误'})
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class': 'register-passwd'}),
                                error_messages={'required': '密码不能为空', 'invalid': '密码格式错误'})
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput(attrs={'class': 'register-passwd'}),
                                error_messages={'required': '密码不能为空', 'invalid': '密码格式错误'})

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(u"两次输入的新密码不一样")
        elif User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError(u"用户名已经存在")
        elif models.UserProfile.objects.filter(name=self.cleaned_data['nickname']).exists():
            raise forms.ValidationError(u"昵称已经存在")
        else:
            cleaned_data = super(UserForm, self).clean()
        return cleaned_data

    @staticmethod
    def pwd_validate(p1, p2):
        return p1 == p2


class UserHeadImgForm(ModelForm):
    class Meta:
        model = models.Article
        fields = ('head_img',)
