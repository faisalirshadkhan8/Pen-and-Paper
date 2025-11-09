from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Category, Tag, Post, Comment, AuthorApplication, UserProfile


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


@admin.register(AuthorApplication)
class AuthorApplicationAdmin(admin.ModelAdmin):
	list_display = ("user", "status", "created_at", "reviewed_by", "reviewed_at")
	list_filter = ("status", "created_at")
	search_fields = ("user__username", "user__email", "reason")
	readonly_fields = ("created_at", "updated_at")
	
	fieldsets = (
		('Application Info', {
			'fields': ('user', 'reason', 'status')
		}),
		('Review Info', {
			'fields': ('reviewed_by', 'reviewed_at', 'admin_notes')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	actions = ['approve_applications', 'reject_applications']
	
	def approve_applications(self, request, queryset):
		"""Approve selected applications and add users to Author group"""
		author_group, _ = Group.objects.get_or_create(name='Author')
		approved_count = 0
		
		for application in queryset.filter(status=AuthorApplication.PENDING):
			# Add user to Author group
			application.user.groups.add(author_group)
			
			# Update application status
			application.status = AuthorApplication.APPROVED
			application.reviewed_by = request.user
			application.reviewed_at = timezone.now()
			application.save()
			
			# Send approval email
			try:
				send_mail(
					subject='Your Author Application Has Been Approved! 🎉',
					message=f'''Hi {application.user.username},

Congratulations! Your application to become an author has been approved.

You can now create and publish posts on our blog platform.

Get started by creating your first post: {request.build_absolute_uri('/post/create/')}

Happy writing!

Best regards,
The Blog Team''',
					from_email=settings.DEFAULT_FROM_EMAIL,
					recipient_list=[application.user.email],
					fail_silently=True,
				)
			except Exception as e:
				pass  # Continue even if email fails
			
			approved_count += 1
		
		self.message_user(request, f'{approved_count} application(s) approved successfully.')
	approve_applications.short_description = "✅ Approve selected applications"
	
	def reject_applications(self, request, queryset):
		"""Reject selected applications"""
		rejected_count = 0
		
		for application in queryset.filter(status=AuthorApplication.PENDING):
			application.status = AuthorApplication.REJECTED
			application.reviewed_by = request.user
			application.reviewed_at = timezone.now()
			application.save()
			
			# Send rejection email
			try:
				send_mail(
					subject='Author Application Update',
					message=f'''Hi {application.user.username},

Thank you for your interest in becoming an author on our blog platform.

After careful review, we are unable to approve your application at this time.

You can submit a new application in the future if you'd like to try again.

Best regards,
The Blog Team''',
					from_email=settings.DEFAULT_FROM_EMAIL,
					recipient_list=[application.user.email],
					fail_silently=True,
				)
			except Exception as e:
				pass  # Continue even if email fails
			
			rejected_count += 1
		
		self.message_user(request, f'{rejected_count} application(s) rejected.')
	reject_applications.short_description = "❌ Reject selected applications"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'email_verified', 'verification_sent_at', 'created_at')
	list_filter = ('email_verified', 'created_at')
	search_fields = ('user__username', 'user__email')
	readonly_fields = ('verification_token', 'created_at', 'updated_at')
	
	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user')

# Register your models here.
