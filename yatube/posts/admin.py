from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'text',
                    'created',
                    'author',
                    'group',)

    search_fields = ('text',)

    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):

    list_display = ('pk',
                    'title',
                    'slug',
                    'description',)

    search_fields = ('title', 'slug',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)