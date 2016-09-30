import Swiper from 'swiper'
import EvEmitter from 'ev-emitter'
import moment from 'moment'
import aja from 'aja'
import xhr from 'xhr'

import Highcharts from 'highcharts'
import Tabs from 'plugins/tabs'

import CommentsWidget from 'jsx/comments-widget'
import HomepageWidget from 'jsx/homepage-widget'
import RatingWidget from 'jsx/rating-widget'

import CSRF_TOKEN from 'csrf'

module.exports = function(){

    // Yandex maps are in global scope
    ymaps = window.ymaps
    moment.locale('ru');

    const ORGANIZATION_ID = document.getElementById('organization-id').value
    const IS_AUTHENTICATED = !!document.getElementById('is-authenticated').value
    const URL_PARTNERS = '/api/partners/'
    const URL_COMMENTS = '/api/comments/'
    const URL_RATING = '/api/rating/'

    var loadBranchesData = new Promise((resolve, reject) => {
        xhr.branches(ORGANIZATION_ID, (data) => resolve(data))
    })
    var loadMap = new Promise((resolve, reject) => {
        ymaps.ready(resolve)

    })
    var loadOrganizationInfo = new Promise((resolve, reject) => xhr.organization(resolve))

    var initMap = Promise.all([loadOrganizationInfo, loadBranchesData, loadMap])


    function init([organizationInfo, branchesList]){
        var branches_map = new ymaps.Map ("branches-map", {
            center: [55.76, 37.64],
            zoom: 7
        });

        function addAddress(address) {
            ymaps.geocode(address).then(
                function (res) {
                    branches_map.geoObjects.add(res.geoObjects);
                },
                function (err) {
                    console.error(err)
                }
            );
        }

        addAddress(organizationInfo.full_address);
        branchesList.results.forEach((branch) => {
            addAddress(branch.full_address)
        })

    }
    initMap.then(init)

    var description_toggler = document.getElementById('toggle-description');
    var description_wrapper = document.getElementById('description-wrapper');
    description_toggler.addEventListener('click', function(event){
       event.preventDefault();
       description_wrapper.classList.contains('open') ? description_wrapper.classList.remove('open') :
               description_wrapper.classList.add('open');
    });

    new HomepageWidget(document.getElementById("partners"),
        {
            // list global business data
            url: URL_PARTNERS + '?organization_id=' + ORGANIZATION_ID,
            is_favorite: false,
            showCategories: false,

            // https://www.squarefree.com/securitytips/web-developers.html#CSRF
            csrf_token: CSRF_TOKEN
        }
    );

    // // Customer comments widget
    CommentsWidget(
            document.getElementById("widget-comments"),
            {
                // url for list/create comments data
                url: URL_COMMENTS,
                organization_id: ORGANIZATION_ID,
                is_authed: true,
                // https://www.squarefree.com/securitytips/web-developers.html#CSRF
                csrf_token: CSRF_TOKEN
            }
    );

    var tabs = new Tabs(document.getElementsByClassName('widget-tabs')[0]);
    var tabs2 = new Tabs(document.getElementsByClassName('comments-tabs')[0]);
    var tabs3 = new Tabs(document.getElementsByClassName('widget-branches')[0]);
    var btn_widget_branches = document.getElementById('btn-widget-branches');

    !!btn_widget_branches && btn_widget_branches.addEventListener('click', function(event){
        this.setAttribute('href', tabs3.getActiveToggler().getAttribute('href'));
    });

    new Highcharts.Chart({
        chart: {
            renderTo: 'container'
        },
        title: {
            text: "{% trans 'Company growth' %}"
        },
        xAxis: {
            type: 'datetime'
        },

        series: [{
            data: [],
            pointStart: Date.UTC(2013, 0, 1),
            pointInterval: 3600 * 1000 * 24 * 30 // one month
        }]
    });
    window.onload = function(){
        new Swiper ('.featured-slider', {
            // Optional parameters
            loop: true,
            autoplay: 3000,
            // If we need pagination
            pagination: '.swiper-pagination'
        });
        new Swiper ('.popular-slider', {
            // Optional parameters
            loop: true,
            autoplay: 2000,
            // If we need pagination
            pagination: '.swiper-pagination'
        });
    };

    function sendForm(form, callback) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function() { // (3)
          if (xhr.readyState != 4) return;
          if (xhr.status != 200) {
              console.log(JSON.parse(xhr.responseText));
              var data = JSON.parse(xhr.responseText);
              showErrors(form, data)
          } else {
              callback && callback(JSON.parse(xhr.responseText))
          }
        };
        xhr.send(formData);
    }

     var image_form = document.getElementById('business_image_upload');
     var image_file = document.getElementById("file_input");
     !!image_file && image_file.addEventListener("change", function(event){
        sendForm(image_form, function(res){
            var imgs_organization = document.getElementsByClassName('img-organization');
            for(var i = 0, l = imgs_organization.length; i < l; i++)
            {
                imgs_organization[i].setAttribute('src', res.image.medium_square_crop);
            }
        });
     });

    new RatingWidget(
        document.getElementById('rating-widget'),
        {
            retrieve_url: URL_RATING + "?organization_id=" + ORGANIZATION_ID,
            vote_url: URL_RATING + "?organization_id=" + ORGANIZATION_ID,
            csrf_token: CSRF_TOKEN,
            social_urls: {
              fb: "/login/facebook/?next=/en/organization/2/",
              vk: "/login/vk-oauth2/?next=/en/organization/2/",
              gp: "/login/google-plus/?next=/en/organization/2/"
            },
            is_authenticated: IS_AUTHENTICATED
        }
    )
}