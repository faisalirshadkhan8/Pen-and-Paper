from django.contrib import admin
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "created_at", "updated_at")
	search_fields = ("name",)
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "created_at", "updated_at")
	search_fields = ("name",)
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "status", "published_at", "created_at")
	list_filter = ("status", "author", "category", "tags")
	search_fields = ("title", "content")
	prepopulated_fields = {"slug": ("title",)}
	autocomplete_fields = ("author", "category", "tags")
	date_hierarchy = "published_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("post", "user", "is_approved", "created_at")
	list_filter = ("is_approved",)
	search_fields = ("content",)

# Register your models here.
