from django.contrib import admin
from  clbbs import models
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title','category','author','pub_date','last_modify','status','priority','thumb_count')
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article','parent_comment','comment_type','comment','user','date','comment_thumb_count')
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','set_as_top_menu','position_index')
admin.site.register(models.Article,ArticleAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.Category,CategoryAdmin)
