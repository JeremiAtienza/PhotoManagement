import os
from pathlib import Path

import cloudinary
from cloudinary import CloudinaryResource, uploader
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.urls import reverse


class LocalCloudinaryResource(CloudinaryResource):
    def __init__(self, public_id=None, format=None, **kwargs):
        super().__init__(public_id=public_id, format=format, **kwargs)
        if self.format is None and self.public_id:
            self.format = Path(self.public_id).suffix.lstrip('.')

    @property
    def url(self):
        return f"{settings.MEDIA_URL}{self.public_id}"

    def get_prep_value(self):
        return self.public_id


class FallbackCloudinaryField(CloudinaryField):
    def _cloudinary_configured(self):
        config = cloudinary.config()
        return bool(config.cloud_name and config.api_key and config.api_secret)

    def _save_locally(self, value):
        if hasattr(value, 'seekable') and value.seekable():
            value.seek(0)

        storage = FileSystemStorage(location=settings.MEDIA_ROOT)
        os.makedirs(storage.path('photo-album-app'), exist_ok=True)
        saved_name = storage.save(f"photo-album-app/{Path(value.name).name}", value)
        return LocalCloudinaryResource(public_id=saved_name)

    def parse_cloudinary_resource(self, value):
        if isinstance(value, LocalCloudinaryResource):
            return value
        if isinstance(value, str) and not value.startswith(('image/', 'raw/', 'video/')):
            return LocalCloudinaryResource(public_id=value)
        return super().parse_cloudinary_resource(value)

    def pre_save(self, model_instance, add):
        value = super(CloudinaryField, self).pre_save(model_instance, add)
        if not isinstance(value, UploadedFile):
            return value

        if self._cloudinary_configured():
            options = {"type": self.type, "resource_type": self.resource_type}
            options.update({key: val(model_instance) if callable(val) else val for key, val in self.options.items()})
            if hasattr(value, 'seekable') and value.seekable():
                value.seek(0)
            instance_value = uploader.upload_resource(value, **options)
        else:
            instance_value = self._save_locally(value)

        setattr(model_instance, self.attname, instance_value)
        metadata = getattr(instance_value, 'metadata', {}) or {}
        if self.width_field:
            setattr(model_instance, self.width_field, metadata.get('width'))
        if self.height_field:
            setattr(model_instance, self.height_field, metadata.get('height'))
        return self.get_prep_value(instance_value)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    is_public = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        permissions = [
            ('moderate_content', 'Can moderate inappropriate content'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'pk': self.pk})


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_photos')
    image = FallbackCloudinaryField('image', folder='photo-album-app/', resource_type='image')
    caption = models.CharField(max_length=255, blank=True)
    is_public = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    moderation_notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('moderate_content', 'Can moderate inappropriate content'),
        ]

    def __str__(self):
        return self.caption or f'Photo {self.pk}'

    def get_absolute_url(self):
        return reverse('photo_edit', kwargs={'pk': self.pk})
