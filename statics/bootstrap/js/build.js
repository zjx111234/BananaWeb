/**
 * Created by Administrator on 2017/2/10 0010.
 */
    function getCsrf(){
        return $("input[name='csrfmiddlewaretoken']").val();
    }

    function GetArticles() {
        var box = $('.wrap-left'),page_num = box.attr('data-page')
            $.post("/clbbs/get_articles/{{ category_obj.id }}/",
                {
                    'page_num':page_num,
                    'csrfmiddlewaretoken':getCsrf()
                },
                function (callback) {
                        callback = jQuery.parseJSON(callback);
                        console.log(callback);
                        $(".wrap-left").append(callback.data);
                        box.attr('data-page',callback.page_num)
                }
            )
         };





