from django import forms

from .models import Album, Photo, Tag


class AlbumForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Summer Travel Highlights'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Add a short summary for this album.'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
        }


class PhotoUploadForm(forms.ModelForm):
    album = forms.ModelChoiceField(queryset=Album.objects.none(), widget=forms.HiddenInput())

    class Meta:
        model = Photo
        fields = ['album', 'image', 'caption', 'is_public', 'tags']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe the photo and add context.'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None:
            self.fields['album'].queryset = Album.objects.none()
            return

        if user.is_superuser or user.groups.filter(name='Album Administrator').exists():
            self.fields['album'].queryset = Album.objects.all()
        else:
            self.fields['album'].queryset = Album.objects.filter(owner=user)


class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['caption', 'is_public', 'tags', 'is_approved', 'moderation_notes']
        widgets = {
            'caption': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Update the photo caption.'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'moderation_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Add notes for reviewers or moderation history.'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        is_admin = user is not None and (user.is_superuser or user.groups.filter(name='Album Administrator').exists())
        if not is_admin:
            self.fields.pop('is_approved', None)
            self.fields.pop('moderation_notes', None)
