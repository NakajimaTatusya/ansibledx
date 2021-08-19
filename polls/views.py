import csv
import os
import io
import json
import logging
import urllib
import socket

from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from django.http import HttpResponseRedirect, HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template import loader
from django.views.generic import ListView
from .models import Choice, Inventory, Question
from .forms import InventoryCreateForm, InventoryCsvUpload
from django.db.models import Max
from polls.function import process_files, write_into_csv


def ClearInventoryFiles():
    """
    ansible host vars 変数ファイルをすべて削除する
    """
    for filename in os.scandir('/home/ceansible/ce_dx_proj/auto-kitting/host_vars'):
        if filename.name.endswith('.yml'):
            os.unlink(filename)


def OutputInventoryFile():
    """
    hosts ファイルを作成する
    """
    const_hosts = """---
  all:
    hosts:
    vars:
      ansible_connection: winrm
      ansible_port: 5985
      ansible_winrm_server_cert_validation: ignore
    children:
      win10_client_kitting:
        hosts:
"""

    const_vars = """---
  ansible_user: %s
  ansible_password: %s
...
"""

    rows = Inventory.objects.all()
    for row in rows:
        # get ip address from hostname
        ipaddrss = ""
        try:
            ipaddrss = socket.gethostbyname(row.hostname)
        except:
            ipaddrss = row.hostname
            logging.exception("get host by %s error." % row.hostname)

        # hosts.yml ファイル用
        const_hosts += "          %s:\n" % ipaddrss

        # host_varsファイル出力
        with open('/home/ceansible/ce_dx_proj/auto-kitting/host_vars/%s.yml' % ipaddrss, 'w') as fhv:
          fhv.write(const_vars % (row.username, row.password))
    const_hosts += "..."

    # hosts.yml 書き出し    
    with open('/home/ceansible/ce_dx_proj/auto-kitting/products/hosts.yml', 'w') as fh:
        fh.write(const_hosts)


def index(request):
    """
    ホームページを表示
    """
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoseNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': '選択されていません',
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def ansible_confirm(request):
    return render(request, 'polls/ansible_test.html', {})


def ansible_powermng_zero(request):
    return render(request, 'polls/ansible_powermng_zero.html', {})


def ansible_winUpdate(request):
    return render(request, 'polls/ansible_winUpdate.html', {})


def ansible_basic(request):
    return render(request, 'polls/ansible_basic.html', {})


def ansible_powermng(request):
    return render(request, 'polls/ansible_powermng.html', {})


def win_ping(request):
    return StreamingHttpResponse(CommandPing())


def win_powermng_zero(request):
    return StreamingHttpResponse(CommandWinPowermngZero())


def win_update(request):
    return StreamingHttpResponse(CommandWinUpdate())


def win_basic(request):
    return StreamingHttpResponse(CommandWinBasic())


def win_powermng(request):
    return StreamingHttpResponse(CommandWinPowermng())


def ansibleplaybook_log_analysis(request):
    return StreamingHttpResponse(CommandAnsilePlayLogAnalysis())


script_parent_path: str = '/home/ceansible/ce_dx_proj/auto-kitting/scripts/'
script_current_dir: str = '/home/ceansible/ce_dx_proj/auto-kitting/'


def CommandPing():
    with Popen(['bash', script_parent_path + 'win_confirm.sh'], \
                cwd=script_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


def CommandWinPowermngZero():
    with Popen(['bash', script_parent_path + 'win_powermng_zero.sh'], \
                cwd=script_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


def CommandWinUpdate():
    with Popen(['bash', script_parent_path + 'win_update.sh'], \
                cwd=script_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


def CommandWinBasic():
    with Popen(['bash', script_parent_path + 'win_basic.sh'], \
                cwd=script_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


def CommandWinPowermng():
    with Popen(['bash', script_parent_path + 'win_powermng.sh'], \
                cwd=script_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


log_analysis_path: str = '/home/ceansible/ce_dx_proj/auto-kitting/ansible_log_analysis/log_decomposition.py'
log_analysis_current_dir: str = '/home/ceansible/ce_dx_proj/auto-kitting/ansible_log_analysis/'


def CommandAnsilePlayLogAnalysis():
    with Popen(['python3', log_analysis_path], \
                cwd=log_analysis_current_dir, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield line
            yield "<br>\n"
            yield " " * 1024


def InventoryUpload(request):
    """
    Inventory情報をCSVで登録
    """
    if request.method == 'POST':
        upload = InventoryCsvUpload(request.POST, request.FILES)

        if upload.is_valid():
            target_list = request.FILES['target_list']
            csv_data = process_files(target_list)
            viewname = write_into_csv(csv_data)
            # output ansible inventory file
            ClearInventoryFiles()
            OutputInventoryFile()
            return redirect(viewname)
        else:
            return render(request, "polls/inventory_upload.html", {'form':upload})
    else:
        upload = InventoryCsvUpload()
        return render(request, "polls/inventory_upload.html", {'form':upload})


def PostExportCsv(request):
    """
    現在のInventory情報をCSVでダウンロード
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = urllib.parse.quote((u'inventory.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
    strio = io.StringIO()
    writer = csv.writer(strio)

    writer.writerow(['HOSTNAME', 'USERNAME', 'PASSWORD'])
    for row in Inventory.objects.all():
        writer.writerow([row.hostname, row.username, row.password])
    response.write(strio.getvalue().encode('utf_8'))
    return response


def ListAnsibleLogs(request):
    dirpath = "/home/ceansible/ansibledx/static/polls/ansible_playlogs/"
    wk_list = sorted(Path(dirpath).iterdir(), key=os.path.getmtime, reverse=True)
    log_list = list(map(lambda x: os.path.basename(x), wk_list))
    return render(request, 'polls/ansible_playbook_log_list.html', {'logs': log_list})


class InventoryList(ListView):
    model = Inventory
    form_class = InventoryCreateForm
    template_name = 'polls/inventorylist.html'
    paginate_by = 10
    ordering = ['order_no']
    context_object_name = 'inventory_list'


    def post(self, request, *args, **kwargs):
        form_inventory_value = [
            self.request.POST.get('host_name', None),
            self.request.POST.get('user_name', None),
            self.request.POST.get('pass_word', None),
        ]
        deletetaget = self.request.POST.get('deletejson', None)
        request.session['form_inventory_value'] = form_inventory_value
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        # 削除処理
        if deletetaget:
            jsonobj = json.loads(deletetaget)
            for element in jsonobj:
                Inventory.objects.filter(hostname=element["host_name"]).delete()

        # 登録、更新処理
        if form_inventory_value[0]:
            new_order_no = Inventory.objects.all().aggregate(Max('order_no'))
            if new_order_no:
                new_order_no = 1
            _ipaddress = ""
            try:
                _ipaddress = socket.gethostbyname(form_inventory_value[0])
            except:
                _ipaddress = form_inventory_value[0]
                logging.exception("get host by %s error." % form_inventory_value[0])
            new_row = Inventory(hostname=form_inventory_value[0], ipaddress=_ipaddress, username=form_inventory_value[1], password=form_inventory_value[2], order_no=new_order_no)
            new_row.save()

        # output ansible inventory file
        ClearInventoryFiles()
        OutputInventoryFile()

        return self.get(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_name = ''
        user_name = ''
        pass_word = ''
        # if 'form_inventory_value' in self.request.session:
        #     form_value = self.request.session['form_inventory_value']
        #     host_name = form_value[0]
        #     user_name = form_value[1]
        #     pass_word = form_value[2]
        default_data = {
            'host_name': host_name,  # ホスト名
            'user_name': user_name,  # ユーザー名
            'pass_word': pass_word,  # パスワード
        }
        inventry_form = InventoryCreateForm(initial=default_data)
        context['inventory_form'] = inventry_form
        return context
