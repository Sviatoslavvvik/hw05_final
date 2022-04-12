from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Группа, к которой будет относиться пост',
                      'image': 'Картинка'}
        labels = {'text': 'Текст поста',
                  'group': 'Группа',
                  'image': 'Картинка'}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        """replace the second name from
        black list on *** """
        data = self.cleaned_data['text']
        black_list = {
            'бузова': '******',
            'донцова': '******',
        }
        data = data.lower()
        temp_data = data
        for second_name, replacing in black_list.items():
            upd_data = temp_data.replace(second_name, replacing)
            temp_data = upd_data
        upd_data = upd_data.capitalize()
        return upd_data
