import aja from 'aja'
import React from 'react'
import ReactDOM from 'react-dom'

import xhr from 'xhr'

import HomepageWidget from 'jsx/homepage-widget'


module.exports = () => {
    var favorites_wrapper = document.getElementById("favorite-brands");
    var main_wrapper = document.getElementById("homepage-brands");
    var categories_sidebar = document.getElementById("categories-sidebar");
    var sidebar_toggler = document.getElementById("sidebar-toggler");
    sidebar_toggler.addEventListener('click', function(event){
        event.preventDefault();
        categories_sidebar.classList.contains('open') ? categories_sidebar.classList.remove('open') :
                categories_sidebar.classList.add('open')
    });

    (function initFavoritesToggler() {
        var toggler = document.getElementById('favorites-toggler');
        toggler.addEventListener('click', function(event){
            event.preventDefault();
            if(this.classList.contains('active'))
            {
                main_wrapper.classList.remove('hidden');
                favorites_wrapper.classList.add('hidden');
                this.classList.remove('active')
            }
            else
            {
                main_wrapper.classList.add('hidden');
                favorites_wrapper.classList.remove('hidden');
                this.classList.add('active')
            }
        });
    })();

    var favoritesWidget = new HomepageWidget(favorites_wrapper,
        {
            // list business data from favorites
            url: '/api/favorites/',  //{% url 'api-organizations-favorites' %}
            is_favorite: true,
            showCategories: false,
            // https://www.squarefree.com/securitytips/web-developers.html#CSRF
            csrf_token: ""
        }
    );


    xhr.categories((data) => {
        var homepageWidget = new HomepageWidget(main_wrapper,
            {
                // list global business data
                url: '/api/organizations/',  // '{% url 'api-organizations-list' %}',
                is_favorite: false,
                categories: data,
                // https://www.squarefree.com/securitytips/web-developers.html#CSRF
                csrf_token: "sdfa"
            }
        )

        document.getElementById('search-input').addEventListener('keyup', function(event){
            if(this.value.trim().length >= 3)
            {
                homepageWidget.updateQueryParams({
                    search: this.value.trim()
                })
            } else if(this.value.trim() == '')
            {
                homepageWidget.updateQueryParams({
                    search: ''
                })
            }
        })

        document.getElementsByClassName('country-radio').forEach.call(function(radio){
            radio.addEventListener('change', function(event){
                var name = this.getAttribute('name'),
                    value = this.getAttribute('value');
                var country_map = {
                    ru: 'RU',
                    hy: 'AM',
                    en: 'GB'
                };
                mainWidget.updateQueryParams({
                    country: country_map[this.getAttribute('value')]
                })
            })
        });

    })

}