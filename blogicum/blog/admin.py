from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        (_('Дополнительные настройки'), {
            'fields': ('is_published',),
            'classes': ('collapse',),
            'description': _('Настройки видимости категории')
        }),
        (_('Мета-данные'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)
    list_editable = ('is_published',)
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        (_('Дополнительные настройки'), {
            'fields': ('is_published',),
            'classes': ('collapse',),
            'description': _('Настройки видимости местоположения')
        }),
        (_('Мета-данные'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'location',
                    'is_published', 'pub_date', 'created_at')
    list_filter = ('is_published', 'category', 'location', 'pub_date')
    search_fields = ('title', 'text', 'author__username', 'author__first_name',
                     'author__last_name')
    list_editable = ('is_published', 'category', 'location')
    raw_id_fields = ('author',)
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'text', 'author')
        }),
        (_('Категория и место'), {
            'fields': ('category', 'location'),
            'classes': ('collapse',),
        }),
        (_('Публикация'), {
            'fields': ('pub_date', 'is_published'),
            'description': _('Настройки публикации')
        }),
        (_('Мета-данные'), {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Добавляем подсказки к полям
        form.base_fields['is_published'].help_text = _(
            'Снимите галочку, чтобы скрыть публикацию.'
        )
        form.base_fields['pub_date'].help_text = _(
            'Если установить дату и время в будущем'
            ' — можно делать отложенные публикации.'
        )
        return form


# Регистрация моделей с кастомными админ-классами
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)

# Настройка заголовков админ-панели
admin.site.site_title = _('Администрирование Блога')
admin.site.site_header = _('Блог - Панель управления')
admin.site.index_title = _('Управление контентом блога')
