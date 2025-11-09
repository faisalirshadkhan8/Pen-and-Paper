from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Category(TimestampedModel):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(max_length=120, unique=True, blank=True)

	class Meta:
		ordering = ["name"]

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return self.name


class Tag(TimestampedModel):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(max_length=60, unique=True, blank=True)

	class Meta:
		ordering = ["name"]

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return self.name


class Post(TimestampedModel):
	DRAFT = "draft"
	PUBLISHED = "published"
	STATUS_CHOICES = [
		(DRAFT, "Draft"),
		(PUBLISHED, "Published"),
	]

	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True, blank=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	content = models.TextField()
	image = models.ImageField(upload_to='posts/', null=True, blank=True)
	category = models.ForeignKey(
		Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
	)
	tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
	published_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-published_at", "-created_at"]
		indexes = [
			models.Index(fields=["status", "published_at"]),
			models.Index(fields=["slug"]),
		]

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse("post-detail", kwargs={"slug": self.slug})

	def __str__(self) -> str:
		return self.title


class Comment(TimestampedModel):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	content = models.TextField()
	is_approved = models.BooleanField(default=True)

	class Meta:
		ordering = ["created_at"]

	def __str__(self) -> str:
		return f"Comment by {self.user} on {self.post}"


class AuthorApplication(TimestampedModel):
	"""Model to track user applications to become authors"""
	PENDING = 'pending'
	APPROVED = 'approved'
	REJECTED = 'rejected'
	
	STATUS_CHOICES = [
		(PENDING, 'Pending Review'),
		(APPROVED, 'Approved'),
		(REJECTED, 'Rejected'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_applications')
	reason = models.TextField(help_text="Why do you want to become an author?")
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
	reviewed_by = models.ForeignKey(
		User, on_delete=models.SET_NULL, null=True, blank=True, 
		related_name='reviewed_applications'
	)
	reviewed_at = models.DateTimeField(null=True, blank=True)
	admin_notes = models.TextField(blank=True, help_text="Internal notes from admin")
	
	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['status', 'created_at']),
		]
	
	def __str__(self):
		return f"{self.user.username} - {self.get_status_display()}"


class UserProfile(TimestampedModel):
	"""Extended user profile for email verification"""
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	email_verified = models.BooleanField(default=False)
	verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	verification_sent_at = models.DateTimeField(null=True, blank=True)
	
	def is_verification_expired(self):
		"""Check if verification link has expired (1 hour)"""
		if not self.verification_sent_at:
			return True
		expiry_time = self.verification_sent_at + timezone.timedelta(hours=1)
		return timezone.now() > expiry_time
	
	def __str__(self):
		return f"{self.user.username} - {'Verified' if self.email_verified else 'Unverified'}"

# Create your models here.
