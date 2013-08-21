define([
    'angular'
    'scripts/controllers/controllers'
    'scripts/directives/directives'
    #'scripts/filters/filters'
    'scripts/services/services'
], (ng)->
    return ng.module('local', [
        'local.controllers'
        'local.directives'
        'local.services'
        #'local.filters'
    ]).config(($routeProvider)->
        $routeProvider
            .when('/', {
                redirectTo: '/login'
            })
            .when('/404/', {
                templateUrl: 'views/404.html'
                controller: 'NotFound'
            })
            .otherwise({
                redirectTo: '/404/'
            })
    )
)
