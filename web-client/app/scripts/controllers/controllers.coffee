define([
    'angular'
    'scripts/services/services'
], (ng, services)->
    return ng.module('local.controllers', ['local.services']).controller({
        Chat: ($scope, MessageService)->
            $scope.messages = MessageService.getMessages()

            $scope.sendMessage = ()->
                MessageService.createMessage({
                    author: $scope.author,
                    text: $scope.text
                })
                $scope.text = ''

            MessageService.bootstrap()

        NotFound: ($scope)->
            $scope.title = '404'
    })
)
