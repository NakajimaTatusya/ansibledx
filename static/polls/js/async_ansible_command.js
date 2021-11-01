$(document).ready(function () {
    $('#run').click(function () {
        if (!confirm("実行します。よろしいですか？")) {
            return;
        }

        $("#output_result").html('')
        $(this).prop("disabled", true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>疎通確認中・・・');
        var lastResLength = 0;
        var timer = null;

        var ajaxReq = $.ajax({
            type: 'GET',
            url: "{% url 'polls:win_ping' %}",
            data: '',
            dataType: 'html',
            contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
            processData: false,
            xhrFields: {
                onloadstart: function () {
                    var xhr = this;
                    var resTextLength = 0
                    timer = setInterval(function () {
                        var textData = xhr.responseText;
                        var newTextData = textData.substring(resTextLength);

                        if (textData.length > resTextLength) {
                            newTextData.split("\n").forEach(function (element) {
                                $("#output_result").html($("#output_result").html() + element.trim());
                                resTextLength = textData.length;
                                var obj = document.getElementById('output_result');
                                obj.scrollTop = obj.scrollHeight;
                            }, 100);
                        }
                    })
                }
            }
        }).then(
            function (data, textStatus, jqXHR) {
                /*成功*/
                setTimeout(() => {
                    clearInterval(timer);
                }, 1000);
                $('button').prop('disabled', false);
                $('button').html('Play - 疎通確認');
            },
            function (jqXHR, textStatus, errorThrown) {
                /*失敗*/
                setTimeout(() => {
                    clearInterval(timer);
                }, 1000);
                $('button').prop('disabled', false);
                $('button').html('Play - 疎通確認');
                alert('失敗：' + jqXHR.status + '：' + textStatus)
            }
        );
    });
});
