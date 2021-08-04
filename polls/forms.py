from django import forms

from .validators import validate_is_csv


class InventoryCreateForm(forms.Form):
    host_name = forms.CharField(
        initial = '',
        label = 'ホスト名',
        required = True,
        max_length = 15,
    )
    user_name = forms.CharField(
        initial = '',
        label = 'ユーザー名',
        required = True,
        max_length = 256,
    )
    pass_word = forms.CharField(
        initial = '',
        label = 'パスワード',
        required = True,
        max_length = 256,
    )


class InventoryCsvUpload(forms.Form):
    target_list = forms.FileField(
        initial='',
        label='ターゲットCSVファイル',
        validators=[validate_is_csv],
        widget=forms.FileInput(attrs={'accept':'.csv'})
    )
