from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from albums.views import AdminAnalyticsView, AlbumCreateView, AlbumDeleteView, AlbumDetailView, AlbumListView, AlbumUpdateView, DashboardView, PhotoDeleteView, PhotoUpdateView, PhotoUploadView
from albums.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', AlbumListView.as_view(), name='album_list'),
    path('albums/create/', AlbumCreateView.as_view(), name='album_create'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album_detail'),
    path('albums/<int:pk>/edit/', AlbumUpdateView.as_view(), name='album_update'),
    path('albums/<int:pk>/delete/', AlbumDeleteView.as_view(), name='album_delete'),
    path('albums/<int:pk>/upload/', PhotoUploadView.as_view(), name='photo_upload'),
    path('photos/<int:pk>/edit/', PhotoUpdateView.as_view(), name='photo_edit'),
    path('photos/<int:pk>/delete/', PhotoDeleteView.as_view(), name='photo_delete'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin-dashboard/', AdminAnalyticsView.as_view(), name='admin_dashboard'),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
]
