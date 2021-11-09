from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    # 例: /polls/
    path('', views.index, name='index'),
    # run Ansible command
    path('ansible/', views.ansible_confirm, name='ansible_confirm'),
    path('ansible/win_ping/', views.win_ping, name='win_ping'),
    path('ansible/winpowermng_zero/', views.ansible_powermng_zero, name='ansible_powermng_zero'),
    path('ansible/win_powermng_zero/', views.win_powermng_zero, name='win_powermng_zero'),
    path('ansible/winupdate/', views.ansible_winUpdate, name='ansible_winUpdate'),
    path('ansible/ansible_winUpdate/', views.win_update, name='win_update'),
    path('ansible/winbasic/', views.ansible_basic, name='ansible_basic'),
    path('ansible/win_basic/', views.win_basic, name='win_basic'),
    path('ansible/winpowermng/', views.ansible_powermng, name='ansible_powermng'),
    path('ansible/win_powermng/', views.win_powermng, name='win_powermng'),
    # インベントリ情報初期化後の一覧画面
    path('ansible/inventorylist/', views.InventoryList.as_view(), name='InventoryList'),
    path('ansible/inventoryupload/', views.InventoryUpload, name='InventoryUpload'),
    path('ansible/inventoryexport/', views.PostExportCsv, name='PostExportCsv'),
    # インベントリ情報初期化
    # path('ansible/init_inventory/', views.InitInventory, name='init_inventory'),
    path('ansible/playbookresult', views.ListAnsibleLogs, name="ListAnsibleLogs"),
    path('ansible/playbookloganalysis/', views.ansibleplaybook_log_analysis, name='ansibleplaybook_log_analysis'),
    # 実行ステータス関係
    path('ansible/playbookstatus', views.test_playbook_status, name='playbook_status'),
    path('ansible/addcmd/<str:commandstring>', views.test_add_task, name='add_command'),
    path('ansible/getstatus/<int:cmdid>', views.test_get_play_status, name='get_status'),

    # 例: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # 例: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # 例: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
