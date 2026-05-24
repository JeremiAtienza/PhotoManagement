from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import AlbumForm, PhotoEditForm, PhotoUploadForm
from .models import Album, Photo


def landing_page(request):
    """Public landing page for unauthenticated users."""
    # Redirect all visitors to the dashboard (no login required)
    return redirect('dashboard')


def is_album_admin(user):
    return user.is_superuser or user.groups.filter(name='Album Administrator').exists()


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your account was created successfully. You can now log in.')
        return response


class AlbumOwnerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        album = self.get_object()
        return is_album_admin(self.request.user) or album.owner == self.request.user


class PhotoOwnerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        photo = self.get_object()
        return is_album_admin(self.request.user) or photo.uploaded_by == self.request.user or photo.album.owner == self.request.user


class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 6

    def get_queryset(self):
        queryset = Album.objects.select_related('owner').prefetch_related('tags', 'photos')
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if is_album_admin(self.request.user):
            return queryset.order_by('-updated_at')

        return queryset.filter(Q(owner=self.request.user) | Q(is_public=True)).distinct().order_by('-updated_at')


class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'albums/album_detail.html'

    def get_queryset(self):
        queryset = Album.objects.select_related('owner').prefetch_related('photos__tags', 'tags')
        if is_album_admin(self.request.user):
            return queryset
        return queryset.filter(Q(owner=self.request.user) | Q(is_public=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = self.object.photos.select_related('uploaded_by').prefetch_related('tags').order_by('-created_at')
        context['photos'] = photos
        context['photo_count'] = photos.count()
        return context


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Album created successfully.')
        return response


class AlbumUpdateView(AlbumOwnerOrAdminMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Album updated successfully.')
        return response


class AlbumDeleteView(AlbumOwnerOrAdminMixin, DeleteView):
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('album_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Album deleted successfully.')
        return response


class PhotoUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Photo
    form_class = PhotoUploadForm
    template_name = 'albums/photo_upload_form.html'
    raise_exception = True

    def get_album(self):
        return Album.objects.get(pk=self.kwargs['pk'])

    def test_func(self):
        album = self.get_album()
        return is_album_admin(self.request.user) or album.owner == self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        return {'album': self.get_album().pk}

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Photo uploaded successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album_id})


class PhotoUpdateView(PhotoOwnerOrAdminMixin, UpdateView):
    model = Photo
    form_class = PhotoEditForm
    template_name = 'albums/photo_edit_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not is_album_admin(self.request.user):
            form.instance.is_approved = self.get_object().is_approved
            form.instance.moderation_notes = self.get_object().moderation_notes
        response = super().form_valid(form)
        messages.success(self.request, 'Photo metadata updated successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album_id})


class PhotoDeleteView(PhotoOwnerOrAdminMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Photo deleted successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('album_detail', kwargs={'pk': self.object.album_id})


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_albums = Album.objects.filter(owner=self.request.user)
        user_photos = Photo.objects.filter(uploaded_by=self.request.user)
        context['album_count'] = user_albums.count()
        context['photo_count'] = user_photos.count()
        context['public_album_count'] = user_albums.filter(is_public=True).count()
        context['pending_review'] = user_photos.filter(is_approved=False).count()
        return context


class AdminAnalyticsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'albums/admin_dashboard.html'
    permission_required = ('albums.view_album', 'albums.delete_album')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_albums = Album.objects.select_related('owner')
        all_photos = Photo.objects.select_related('album', 'uploaded_by')
        context['album_count'] = all_albums.count()
        context['photo_count'] = all_photos.count()
        context['public_album_count'] = all_albums.filter(is_public=True).count()
        context['pending_review'] = all_photos.filter(is_approved=False).count()
        context['admin_users'] = Group.objects.get(name='Album Administrator').user_set.count()
        return context
