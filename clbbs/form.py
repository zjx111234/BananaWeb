from django.forms import ModelForm
from django import forms
from clbbs import models

#from django.contrib.auth.forms.UserCreationForm


class ArticleModelForm(ModelForm):
    class Meta:
        model = models.Article
        exclude = ('author','pub_date','priority','thumb_count')

    def __init__(self,*args,**kwargs):
        super(ArticleModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = '请输入标题'
        self.fields['brief'].widget.attrs['placeholder'] = '请输入文章简介'

        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            class_name = 'publish-'+field_name
            field.widget.attrs.update({'class': class_name})


class User(forms.Form):
    username = forms.CharField(label='用户名', max_length=100,widget=forms.TextInput(attrs={'class':'register-name'}), error_messages={'required':('用户名不能为空'),'invalid':'用户名格式错误'})
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class':'register-passwd'}), error_messages={'required':('密码不能为空'),'invalid':'密码格式错误'})
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput(attrs={'class':'register-passwd'}), error_messages={'required':('密码不能为空'),'invalid':'密码格式错误'})
    nickname = forms.CharField(label='昵称', widget=forms.TextInput(attrs={'class':'register-nickname'}), error_messages={'required':('昵称不能为空'),'invalid':'昵称格式错误'})
    email = forms.EmailField(label='邮箱')
    head_img = forms.ImageField(label='头像', widget=forms.FileInput(attrs={'class':'register-img'}),error_messages={'required':('请上传头像'),'invalid':'头像格式错误'})

    def pwd_validate(self, p1, p2):
        return p1 == p2



