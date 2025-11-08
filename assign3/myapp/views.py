from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .models import Post, Comment, Category, Tag


class HomeView(LoginRequiredMixin, ListView):
	"""Home page showing published posts - requires login."""
	model = Post
	template_name = 'home.html'
	context_object_name = 'posts'
	paginate_by = 10
	login_url = '/accounts/login/'

	def get_queryset(self):
		qs = Post.objects.select_related('author', 'category').prefetch_related('tags').filter(status=Post.PUBLISHED)
		q = self.request.GET.get('q')
		cat = self.request.GET.get('category')
		tag = self.request.GET.get('tag')
		if q:
			qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
		if cat:
			qs = qs.filter(category__slug=cat)
		if tag:
			qs = qs.filter(tags__slug=tag)
		return qs.distinct().order_by('-published_at', '-created_at')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['categories'] = Category.objects.order_by('name')
		ctx['tags'] = Tag.objects.order_by('name')
		ctx['current_q'] = self.request.GET.get('q', '')
		ctx['current_category'] = self.request.GET.get('category', '')
		ctx['current_tag'] = self.request.GET.get('tag', '')
		return ctx


class PostDetailView(DetailView):
	model = Post
	template_name = 'post_detail.html'
	context_object_name = 'post'
	slug_field = 'slug'
	slug_url_kwarg = 'slug'

	def get_queryset(self):
		qs = Post.objects.select_related('author', 'category').prefetch_related('tags', 'comments__user')
		# Allow viewing drafts if you're the author or staff/superuser
		if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser):
			return qs
		# Filter by published for anonymous and regular users, but allow authors to see own drafts
		return qs.filter(
			Q(status=Post.PUBLISHED) | Q(author=self.request.user)
		) if self.request.user.is_authenticated else qs.filter(status=Post.PUBLISHED)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['comments'] = self.object.comments.filter(is_approved=True).select_related('user')
		return ctx


class CommentCreateView(LoginRequiredMixin, View):
	def post(self, request, slug):
		post = get_object_or_404(Post, slug=slug, status=Post.PUBLISHED)
		content = request.POST.get('content', '').strip()
		if content:
			Comment.objects.create(post=post, user=request.user, content=content, is_approved=True)
		return redirect(post.get_absolute_url())


class RoleRequiredMixin(UserPassesTestMixin):
	"""Basic role mixin: allow superuser/staff or user in Author group."""
	def test_func(self):
		u = self.request.user
		if not u.is_authenticated:
			return False
		if u.is_superuser or u.is_staff:
			return True
		return u.groups.filter(name__in=["Author", "Admin"]).exists()


class PostCreateView(RoleRequiredMixin, LoginRequiredMixin, View):
	def get(self, request):
		ctx = {
			'mode': 'create',
			'categories': Category.objects.order_by('name'),
			'tags': Tag.objects.order_by('name'),
		}
		return render(request, 'post_form.html', ctx)

	def post(self, request):
		title = request.POST.get('title','').strip()
		content = request.POST.get('content','').strip()
		category_slug = request.POST.get('category')
		tag_slugs = request.POST.getlist('tags')
		status = request.POST.get('status','draft')
		image = request.FILES.get('image')
		if title and content:
			post = Post(author=request.user, title=title, content=content, status=status)
			# Set published_at for new published posts
			if status == Post.PUBLISHED:
				post.published_at = timezone.now()
			if category_slug:
				post.category = Category.objects.filter(slug=category_slug).first()
			post.save()
			if tag_slugs:
				post.tags.set(Tag.objects.filter(slug__in=tag_slugs))
			if image:
				post.image = image
				post.save()
			return redirect(post.get_absolute_url())
		ctx = {
			'mode': 'create',
			'error': 'Title and content required.',
			'categories': Category.objects.order_by('name'),
			'tags': Tag.objects.order_by('name'),
		}
		return render(request, 'post_form.html', ctx)


class PostUpdateView(RoleRequiredMixin, LoginRequiredMixin, View):
	def get_object(self):
		return get_object_or_404(Post, slug=self.kwargs['slug'])

	def user_can_edit(self, post):
		u = self.request.user
		if u.is_superuser or u.is_staff:
			return True
		if post.author_id == u.id and u.groups.filter(name__in=["Author", "Admin"]).exists():
			return True
		return False

	def get(self, request, slug):
		post = self.get_object()
		if not self.user_can_edit(post):
			return redirect(post.get_absolute_url())
		ctx = {
			'mode': 'edit',
			'post': post,
			'categories': Category.objects.order_by('name'),
			'tags': Tag.objects.order_by('name'),
		}
		return render(request, 'post_form.html', ctx)

	def post(self, request, slug):
		post = self.get_object()
		if not self.user_can_edit(post):
			return redirect(post.get_absolute_url())
		title = request.POST.get('title','').strip()
		content = request.POST.get('content','').strip()
		status = request.POST.get('status','draft')
		category_slug = request.POST.get('category')
		tag_slugs = request.POST.getlist('tags')
		image = request.FILES.get('image')
		if title and content:
			post.title = title
			post.content = content
			post.status = status
			if status == Post.PUBLISHED and not post.published_at:
				post.published_at = timezone.now()
			if category_slug:
				post.category = Category.objects.filter(slug=category_slug).first()
			if tag_slugs:
				post.tags.set(Tag.objects.filter(slug__in=tag_slugs))
			if image:
				post.image = image
			post.save()
			return redirect(post.get_absolute_url())
		ctx = {
			'mode': 'edit',
			'post': post,
			'error': 'Title and content required.',
			'categories': Category.objects.order_by('name'),
			'tags': Tag.objects.order_by('name'),
		}
		return render(request, 'post_form.html', ctx)


class PostDeleteView(RoleRequiredMixin, LoginRequiredMixin, View):
	def get_object(self):
		return get_object_or_404(Post, slug=self.kwargs['slug'])

	def user_can_delete(self, post):
		u = self.request.user
		if u.is_superuser or u.is_staff:
			return True
		if post.author_id == u.id and u.groups.filter(name__in=["Author", "Admin"]).exists():
			return True
		return False

	def get(self, request, slug):
		post = self.get_object()
		if not self.user_can_delete(post):
			return redirect(post.get_absolute_url())
		return render(request, 'confirm_delete.html', {'post': post})

	def post(self, request, slug):
		post = self.get_object()
		u = request.user
		if self.user_can_delete(post):
			post.delete()
			return redirect('post-list')
		return redirect(post.get_absolute_url())


class DashboardView(RoleRequiredMixin, LoginRequiredMixin, ListView):
	template_name = 'dashboard.html'
	context_object_name = 'posts'
	paginate_by = 15

	def get_queryset(self):
		u = self.request.user
		base = Post.objects.select_related('category').prefetch_related('tags')
		if u.is_superuser or u.is_staff:
			return base.order_by('-created_at')
		return base.filter(author=u).order_by('-created_at')

