import os
import signal
import threading
import time

from .models import PlaybookStatus
from datetime import datetime
from django.conf import settings
from subprocess import Popen, STDOUT, DEVNULL


"""
●主なシグナル
名前	番号	動作（※）	意味
SIGHUP	1	Term	制御端末の切断（ハングアップ）、仮想端末の終了
SIGINT	2	Term	キーボードからの割り込みシグナル（通常は［CTRL］＋［C］）
SIGQUIT	3	Core	キーボードによる中止シグナル（通常は［CTRL］＋［\］）
SIGFPE	8	Core	不正な浮動小数点演算（ゼロ除算やオーバーフローなど）の発生
SIGKILL	9	Term	強制終了シグナル（KILLシグナル）
SIGSEGV	11	Core	不正なメモリ参照の発生
SIGPIPE	13	Term	読み手のいないパイプへの書き込み（通常はこのシグナルを受け取ると即時終了する）
SIGALRM	14	Term	タイマー（Alarm）による終了
SIGTERM	15	Term	終了シグナル（「kill」コマンドのデフォルトシグナル）
SIGCHLD	17	Ignore	子プロセスの状態（終了、停止または再開）が変わった
SIGCONT	18	Cont	一時停止しているジョブへの再開シグナル
SIGSTOP	19	Stop	一時停止シグナル
SIGTSTP	20	Stop	端末からの一時停止シグナル（通常は［CTRL］＋［Z］）
SIGTTIN	21	Stop	バックグラウンドジョブ／プロセスのキーボード入力待ち
SIGTTOU	22	Stop	バックグラウンドジョブ／プロセスの端末出力待ち
SIGXCPU	24	Core	CPU時間制限を越えた
SIGXFSZ	25	Core	ファイルサイズ制限を越えた
SIGWINCH	28	Ignore	ウィンドウのサイズが変更された
"""

class AnsiblePlaybook(threading.Thread):


    def __init__(self, cmdno) -> None:
        super(AnsiblePlaybook, self).__init__()
        self.command_no = cmdno
        self.stop_event = threading.Event()
        self.setDaemon(False)


    def run(self) -> None:
        print(datetime.now())
        command_row = PlaybookStatus.objects.get(commandid=self.command_no)
        proc = Popen(['bash', settings.SCRIPT_PARENT_PATH + command_row.command], \
                    cwd=settings.SCRIPT_CURRENT_DIR, \
                    stdin=DEVNULL, stdout=None, stderr=STDOUT, bufsize=0)
        command_row.processid = proc.pid
        command_row.starttiming = datetime.now()
        command_row.playbookprogress = True
        command_row.save()

        try:
            while proc.poll() == None:
                time.sleep(1)
            # output, errors = p.communicate()
            command_row = PlaybookStatus.objects.get(commandid=self.command_no)
            if proc.returncode == 0:
                command_row.endtiming = datetime.now()
                command_row.playbookprogress = False
                command_row.playbookstatus = PlaybookStatus.PlaybookStatus.SUCCEED._value_
            else:
                command_row.endtiming = datetime.now()
                command_row.playbookprogress = False
                command_row.playbookstatus = PlaybookStatus.PlaybookStatus.FAILED._value_
            command_row.save()
        except Exception as ex:
            raise ex


    def cancel(self) -> None:
        try:
            command_row = PlaybookStatus.objects.get(commandid=self.command_no)
            os.kill(command_row.processid, signal.SIGTERM)
            # need psutil
            # p = psutil.Process(pid)
            # p.terminate()  #or p.kill()
            command_row.endtiming = datetime.now()
            command_row.playbookprogress = False
            command_row.playbookstatus = PlaybookStatus.PlaybookStatus.CANCEL._value_
            command_row.save()
        except Exception as ex:
            raise ex
