define([
    'uuid'
    'angular'
    'scripts/socket'
], (uuid, ng, socket)->
    return ng.module('local.services', []).factory({
        MessageService: ($rootScope)->
            messages = []

            socket.chat.on('message:created', (data)->
                $rootScope.$apply(->
                    found = false

                    for message in messages
                        if message.client_id == data.client_id
                            message.needsConfirm = false
                            found = true
                            break

                    if not found
                        messages.push(data.message)
                )
            )

            socket.chat.on('error', ->
                $rootScope.$apply(->
                    for message in messages
                        if message.needsConfirm
                            message.error = true
                )
            )

            socket.chat.on('message:list', (messageList)->
                $rootScope.$apply(->
                    for message in messageList
                        messages.push(message)
                )
            )

            return {
                getMessages: ()->
                    return messages

                createMessage: (messageObject)->
                    messageObject.needsConfirm = true
                    messageObject.client_id = uuid()

                    messages.push(messageObject)
                    socket.chat.emit('message:create', messageObject)

                bootstrap: ->
                    socket.chat.emit('bootstrap')
            }
    })
)
