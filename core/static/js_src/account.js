import Dropzone from 'dropzone'

import Switcher from 'plugins/switcher'
import Alert from 'plugins/alert'

import CSRF_TOKEN from 'csrf'

var API_TEMP_FILE_URL = '/api/files/temp/'
var API_PROFILE_URL = '/api/profile/'

module.exports = () => {

    Dropzone.autoDiscover = false;
    var userpicDropzone = new Dropzone("#userpic-dropzone",
            {
                url: API_TEMP_FILE_URL,
                previewTemplate: '<div></div>',
                headers: {
                    "X-CSRFToken": CSRF_TOKEN
                }
            }
    );
    userpicDropzone.on("addedfile", function(file) { });
    userpicDropzone.on("success", function(file, res) {
        aja().url(API_PROFILE_URL)
                .header('X-Requested-With', 'XMLHttpRequest')
            .data({
                userpic_url: res.results[0].name,
                csrfmiddlewaretoken: CSRF_TOKEN
            }).method("POST").on('success', function(res){
                console.log(res);
                var img_userpics = document.getElementsByClassName('img-profile-userpic');
                for(var i = 0, l = img_userpics.length; i < l; i++)
                {
                    img_userpics[i].setAttribute('src', res.userpic.thumbnail);
                }
            }).go();
     });

    var organizationLogoDropzone = new Dropzone("#organization-dropzone",
            {
                url: API_TEMP_FILE_URL,
                previewTemplate: '<div></div>',
                headers: {
                    "X-CSRFToken": CSRF_TOKEN
                }
            }
    );
    organizationLogoDropzone.on("addedfile", function(file) { });
    organizationLogoDropzone.on("success", function(file, res) {
        document.getElementById('logo-temp-path').value = res.results[0].name;
        document.getElementById('organization-logo-preview').setAttribute('src', res.results[0].url)
    });

    function formGroupError(form_group, message)
    {
        form_group.classList.add("has-error");
        var help_block = form_group.getElementsByClassName("help-block");
        if(help_block.length)
        {
            help_block[0].innerHTML =message;
        }
    }

    function cleanInputError(event_or_input)
    {
        var input = !!event_or_input.target ? event_or_input.target : event_or_input;
        var form_group = input.parentNode.classList.contains('form-group') ?
                    input.parentNode :
                    input.parentNode.parentNode;

        form_group.classList.remove("has-error");
        var help_block = form_group.getElementsByClassName("help-block");
        if(help_block.length)
        {
            help_block[0].innerHTML = "";
        }
        if(event_or_input.target)
        {
            this.removeEventListener('keyup', cleanInputError)
        }
    }

    function cleanFormErrors(form)
    {
        var inputs = form.getElementsByClassName("form-control");
        for(var i = 0, l = inputs.length; i < l; i++)
        {
            var input = inputs[i];
            cleanInputError(input);
        }
    }

    function showFormErrors(form, data)
    {
        var inputs = form.getElementsByClassName("form-control");
        for(var i = 0, l = inputs.length; i < l; i++)
        {
            var name = inputs[i].name,
                input = inputs[i];
            if(data.hasOwnProperty(name))
            {
                var parent = input.parentNode.classList.contains('form-group') ?
                        input.parentNode :
                        input.parentNode.parentNode;
                formGroupError(parent, data[name]);
                input.addEventListener('keyup', cleanInputError);
            }
        }
    }

    function sendForm(form, callback) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function() { // (3)
          if (xhr.readyState != 4) return;
          if (xhr.status != 200) {
              var data = JSON.parse(xhr.responseText);
              showFormErrors(form, data)
          } else {
              callback && callback.call(form, xhr.responseText);
          }
        };
        xhr.send(formData);
    }
    function cleanForm(form){
        var inputs = form.getElementsByClassName("form-control");
        for(var i = 0, l = inputs.length; i < l; i++)
        {
            if(inputs[i].value) inputs[i].value = "";
        }
    }
    var account_switcher = document.getElementById('account-tabs-swicher');
    var account_tabs = document.getElementById('account-tabs');
    new Switcher(account_switcher, account_tabs);

    var organization_form = document.getElementById("organization-form");
    organization_form.addEventListener('submit', function(event){
        event.preventDefault();
        sendForm(this, function(response){
            new Alert(this, {
                text: "Organization info has been saved"
            })
        });
    });

    var password_link = document.getElementById("change-password-link");
    var password_form = document.getElementById("password-form");
    var password_modal = null;
    password_link.addEventListener('click', function(event){
        event.preventDefault();
        if(password_modal)
        {
            password_modal.show();
        }
        else
        {
            password_modal = new Simodal({
                content: password_form,
                modalClass: "simodal modal-password"
            });
        }
    });

    password_form.addEventListener('submit', function(event){
        event.preventDefault();
        sendForm(this, function(){
            new Alert(this, {
                text: "New password has been set"
            });
            cleanForm(this);
        });
    });

    var profile_form = document.getElementById("profile-form");
    profile_form.addEventListener('submit', function(event){
        event.preventDefault();
        sendForm(this, function(){
            new Alert(this, {
                text: "Profile info saved"
            })
        });
    });
}