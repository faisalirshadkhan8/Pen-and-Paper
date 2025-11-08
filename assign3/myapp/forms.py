from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'status', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        help_texts = {
            'tags': 'Hold Ctrl (Windows) or Cmd (Mac) to select multiple tags',
            'status': 'Published posts are visible to everyone. Drafts are only visible to you.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category and image optional
        self.fields['category'].required = False
        self.fields['image'].required = False
        self.fields['tags'].required = False
        
        # Add empty option for category
        self.fields['category'].empty_label = '-- Select Category (Optional) --'


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts."""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            }),
        }
        labels = {
            'content': 'Your Comment'
        }
