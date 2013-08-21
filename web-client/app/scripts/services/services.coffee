define([
    'uuid'
    'angular'
    'scripts/io'
], (uuid, ng, io)->
    return ng.module('local.services', []).factory({
        MessageService: ($rootScope)->
            messages = []

            io.chat.on('message:created', (newMessage, clientId)->
                $rootScope.$apply(->
                    found = false

                    for message in messages
                        if message.clientId == clientId
                            message.needsConfirm = false
                            found = true
                            break

                    if not found
                        messages.push(newMessage)
                )
            )

            io.chat.on('error', ->
                $rootScope.$apply(->
                    for message in messages
                        if message.needsConfirm
                            message.error = true
                )
            )

            io.chat.on('bootstrap', (messageList)->
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
                    messageObject.clientId = uuid()

                    messages.push(messageObject)
                    io.chat.emit('message:create', messageObject)

                bootstrap: ->
                    io.chat.emit('bootstrap')
            }
    })
)
