import datetime
from enum import unique
from os import name

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Inventory(models.Model):
    # hostname
    hostname = models.CharField(primary_key=True, max_length=15)
    # ipaddress
    ipaddress = models.CharField(max_length=15, null=True)
    # WinRM接続用ユーザー名
    username = models.CharField(max_length=256, null=True)
    # パスワード
    password = models.CharField(max_length=256, null=True)
    # 順番
    order_no = models.IntegerField(default=0)

    def __str__(self):
        return self.hostname

class PlaybookStatus(models.Model):
    # 状態管理
    class PlaybookStatus(models.Choices):
        SUCCEED = 0
        FAILED = 1
        CANCEL = 2

    # command id
    commandid = models.AutoField(primary_key=True, null=False, name="commandid")
    # command
    command = models.CharField(max_length=1024, null=False, name="command")
    # process id
    processid = models.IntegerField(name="processid")
    # 開始日時
    satarttiming = models.DateTimeField(null=True, name="starttiming")
    # 終了日時
    endtiming = models.DateTimeField(null=True, name="endtiming")
    # 進捗(停止：False、処理中：True)
    playbookprogress = models.BooleanField(default=False, null=False, name="playbookprogress")
    # 状態
    playbookstatus = models.IntegerField(choices=PlaybookStatus.choices, name="playbookstatus")

    def __str__(self) -> str:
        return self.command
