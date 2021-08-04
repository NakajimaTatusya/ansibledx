import os
from django.core.exceptions import ValidationError

def validate_is_csv(value):
    ext = (os.path.splitext(value.name))[1]

    if not ext.lower() in ['.csv', '.CSV']:
        raise ValidationError('CSVファイル[文字コード：UTF-8, 改行コード：CR+LF]のみが有効です')
