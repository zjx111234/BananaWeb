function getCsrf(){
    return $("input[name='csrfmiddlewaretoken']").val();
}


$(function () {
    H_login = {};
    H_login.openLogin = function(){
        $('.login-link-box a').click(function(){
            $('.login').show();
            $('.login-bg').show();
        });
        $('.btn-link ').click(function(){
            $('.login').show();
            $('.login-bg').show();
        });
    };
    H_login.closeLogin = function(){
        $('.close-login').click(function(){
            $('.login').hide();
            $('.login-bg').hide();
        });
    };
    H_login.loginForm = function () {
        $("#login-button-submit").on('click',function(){
              var username = $("#username");
              var usernameValue = $("#username").val();
              var password = $("#password");
              var passwordValue = $("#password").val();
            if(usernameValue == ""){
                 document.getElementById('re-msg').innerText="用户名不能为空";
                username.focus();
                return false;
            }else if(usernameValue.length > 15){
                document.getElementById('re-msg').innerText="用户名长度不能大于15字符";
                username.focus();
                return false;
            }else if(passwordValue == ""){
                document.getElementById('re-msg').innerText="密码不能为空";
                password.focus();
                return false;
            }else if(passwordValue.length < 6 || passwordValue.length > 30){
                document.getElementById('re-msg').innerText="密码长度不能小于6或大于30位字符";
                password.focus();
                return false;
            }else{
                $.post('/login/',
                {
                    'username':usernameValue,
                    'password':passwordValue,
                    'csrfmiddlewaretoken':getCsrf()
                },//end post args
                function(callback) {
                    callback = jQuery.parseJSON(callback);
                    if(callback.success=='success'){
                        location.reload();
                    }
                    else if(callback.success=='failed'){
                        document.getElementById('re-msg').innerText="用户名密码错误";
                    }

                })

                //setTimeout(function(){
                //    $('.login').hide();
               //     $('.login-bg').hide();
               //     $('.list-input').val('');
              //  },2000);
            }
        });
    };
    H_login.run = function () {
        this.closeLogin();
        this.openLogin();
        this.loginForm();
    };
    H_login.run();
});


