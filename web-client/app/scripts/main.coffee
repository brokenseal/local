require.config({
    paths: {
        angular: 'bower_components/angular/angular'
        angular_ui: 'bower_components/angular-ui/build/angular-ui'
        angular_ui_bootstrap_dropdown: 'bower_components/angular-ui-bootstrap/src/dropDownToggle/dropDownToggle'
        angular_socket_io: 'bower_components/angular-socket-io/socket'
        ng_resource: 'bower_components/angular-resource/angular-resource'
        ng_cookies: 'bower_components/angular-cookies/angular-cookies'
        ng_sanitize: 'bower_components/angular-sanitize/angular-sanitize'
        io: 'bower_components/socket.io-client/dist/socket.io'
        sockjs: 'bower_components/sockjs-client/lib/sockjs'
        uuid: 'bower_components/node-uuid/uuid'

        lodash: 'bower_components/lodash/lodash'
    }
    baseUrl: ''
    shim: {
        angular : {
            exports : 'angular'
        }
        angularMocks: {
            deps: ['angular']
            exports: 'angular.mock'
        }
        angular_ui: {
            deps: ['angular']
        }
        angular_socket_io: {
            deps: ['angular', 'io']
        }
        angular_ui_bootstrap_dropdown: {
            deps: ['angular']
        }
        ng_sanitize: {
            deps: ['angular']
            exports: 'angular.sanitize'
        }
        lodash: {
            exports: '_'
        }
        io: {
            exports: 'io'
        }
        uuid: {
            exports: 'uuid'
        }
    }
    priority: [
        "angular"
    ]
})

require([
    'angular'
    'io'
    'angular_socket_io'
    'scripts/app'
], (ng, io, ng_socket_io, app)->
    ng.bootstrap(document, [app['name']])
)
