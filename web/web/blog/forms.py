"""Public."""
from django import forms
from .models import Blog, Entry
from .validators import validate_title
from web.users.models import User


class BlogForm(forms.ModelForm):
    """Blog form."""

    def __init__(self, *args, **kwargs):
        """__init__."""
        super(BlogForm, self).__init__(*args, **kwargs)
        # Assign validate_title validator to other fields in forms
        self.fields["tag_line"].validators.append(validate_title)

    def clean_title(self):
        """Docstring."""
        title = self.cleaned_data["title"]
        # Any validator
        # If failed, raise form.ValidationError("msg")
        return title

    def clean(self):
        """Docstring."""
        cleaned_data = super(BlogForm, self).clean()
        title = cleaned_data.get("title", "")
        tag_line = cleaned_data.get("tag_line", "")

        # tag_line should the same title
        if not title == tag_line:
            msg = "The title should same the tag line."
            raise forms.ValidationError(msg)
        return cleaned_data

    class Meta:
        """Docstring."""

        model = Blog
        fields = ["title", "tag_line", "entries_per_page", "recents", "recent_comments"]


class EntryForm(forms.ModelForm):
    """docstring for EntryForm."""

    def __init__(self, *args, **kwargs):
        """___init__."""
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.filter(is_staff=True)

    title = forms.CharField(max_length=100,
                            required=False,
                            widget=forms.TextInput(attrs={'size': '40'}))

    class Meta:
        """Docstring."""

        model = Entry
        exclude = ['slug', 'summary']


class CommentForm(forms.Form):
    """docstring for CommentForm."""

    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea'}),
        label='Comment')
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'textfield'}))
    url = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'textfield'}))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'textfield'}))


class SearchForm(forms.Form):
    """Docstring for SearchForm."""

    queryset = forms.CharField(label='Query')
