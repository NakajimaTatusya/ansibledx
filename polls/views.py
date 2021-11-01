import csv
import os
import io
import json
import logging
import re
import urllib
import socket

from .models import Choice, Inventory, Question
from .forms import InventoryCreateForm, InventoryCsvUpload
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template import loader
from django.views.generic import ListView
from django.db.models import Max
from polls.playbook import AnsiblePlaybook
from polls.function import process_files, write_into_csv, generate_kitting_inventory, purge_host_variable_files, generate_host_variable_files
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, DEVNULL


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
    ap = AnsiblePlaybook(1)
    ap.start()
    return HttpResponse("win_ping start.")


def win_powermng_zero(request):
    ap = AnsiblePlaybook(2)
    ap.start()
    return HttpResponse("Starts the Windows power management zero setting.")


def win_update(request):
    return StreamingHttpResponse(CommandWinUpdate())


def win_basic(request):
    return StreamingHttpResponse(CommandWinBasic())


def win_powermng(request):
    return StreamingHttpResponse(CommandWinPowermng())


def ansibleplaybook_log_analysis(request):
    return StreamingHttpResponse(CommandAnsilePlayLogAnalysis())


def CommandPing():
    with Popen(['bash', settings.SCRIPT_PARENT_PATH + 'win_confirm.sh'], \
                cwd=settings.SCRIPT_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


def CommandWinPowermngZero():
    with Popen(['bash', settings.SCRIPT_PARENT_PATH + 'win_powermng_zero.sh'], \
                cwd=settings.SCRIPT_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


def CommandWinUpdate():
    with Popen(['bash', settings.SCRIPT_PARENT_PATH + 'win_update.sh'], \
                cwd=settings.SCRIPT_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


def CommandWinBasic():
    with Popen(['bash', settings.SCRIPT_PARENT_PATH + 'win_basic.sh'], \
                cwd=settings.SCRIPT_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


def CommandWinPowermng():
    with Popen(['bash', settings.SCRIPT_PARENT_PATH + 'win_powermng.sh'], \
                cwd=settings.SCRIPT_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


def CommandAnsilePlayLogAnalysis():
    with Popen(['python3', settings.LOG_ANALYSIS_PATH], \
                cwd=settings.LOG_ANALYSIS_CURRENT_DIR, \
                stdin=DEVNULL, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            yield "{0}<br>{1}\n".format(line, (" " * 1024))


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
            # host変数ファイルの削除と、Inventoryファイルの生成とhost変数ファイルの生成
            purge_host_variable_files()
            generate_kitting_inventory(p_flag_netbios=settings.FLAG_NETBIOS)
            generate_host_variable_files(p_flag_netbios=settings.FLAG_NETBIOS)
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

    writer.writerow(['ORDERNO', 'HOSTNAME', 'USERNAME', 'PASSWORD'])
    for row in Inventory.objects.order_by('order_no').all():
        writer.writerow([row.order_no, row.hostname, row.username, row.password])
    response.write(strio.getvalue().encode('utf_8'))
    return response


def ListAnsibleLogs(request):
    wk_list = []
    wk_list = sorted(Path(settings.ANSIBLE_LOG_LIST_DIR).iterdir(), key=os.path.getmtime, reverse=True)
    log_list = list(map(lambda x: os.path.basename(x), wk_list))
    # task_result ファイルのみを表示する
    log_list = [x for x in log_list if re.match(r'task_result.*\.html', os.path.basename(x))]
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

        # host変数ファイルの削除と、Inventoryファイルの生成とhost変数ファイルの生成
        purge_host_variable_files()
        generate_kitting_inventory(p_flag_netbios=settings.FLAG_NETBIOS)
        generate_host_variable_files(p_flag_netbios=settings.FLAG_NETBIOS)

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
