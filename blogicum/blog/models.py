from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class Location(models.Model):
    name = models.CharField(max_length=256, verbose_name=_("Название места"))
    is_published = models.BooleanField(
        default=True,
        verbose_name=_("Опубликовано"),
        help_text=_("Снимите галочку, " "чтобы скрыть публикацию."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Добавлено"))

    class Meta:
        verbose_name = _("местоположение")
        verbose_name_plural = _("Местоположения")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Идентификатор"),
        help_text=_(
            "Идентификатор страницы для URL;"
            " разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_("Опубликовано"),
        help_text=_("Снимите галочку, чтобы скрыть публикацию."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Добавлено"))

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("Категории")
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=256, verbose_name=_("Заголовок"))
    text = models.TextField(verbose_name=_("Текст"))
    pub_date = models.DateTimeField(
        verbose_name=_("Дата и время публикации"),
        help_text=_(
            "Если установить дату и время в будущем"
            " — можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Автор публикации"),
        related_name="posts",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Местоположение"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Категория"),
        related_name="posts",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_("Опубликовано"),
        help_text=_("Снимите галочку, чтобы скрыть публикацию."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_("Добавлено"))
    image = models.ImageField(
        upload_to="posts/", null=True, blank=True,
        verbose_name=_("Изображение")
    )

    class Meta:
        verbose_name = _("публикация")
        verbose_name_plural = _("Публикации")
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # Связь с пользователем
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("комментарий")
        verbose_name_plural = _("Комментарии")
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
