from django.urls import path
from .views import (
    HomeView,
    PostDetailView,
    CommentCreateView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    DashboardView,
    UserDashboardView,
    ApplyAuthorView,
)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('my-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('apply-author/', ApplyAuthorView.as_view(), name='apply-author'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<slug:slug>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('post/<slug:slug>/edit/', PostUpdateView.as_view(), name='post-edit'),
    path('post/<slug:slug>/delete/', PostDeleteView.as_view(), name='post-delete'),
]
