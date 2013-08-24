define([
    'io'
    'scripts/settings'
], (io, settings)->
    socket = new SockJS(settings.getBaseUrl() + 'chat')
    onEventCallbacks = {}
#    socket.onopen = ()->
#        console.log("onopen")

    socket.onmessage = (message)->
        if message.data.name of onEventCallbacks
            onEventCallbacks[message.data.name](message.data.data)

    return {
        chat: {
            emit: (name, data)->
                socket.send(JSON.stringify(
                    name: name
                    data: data
                ))
            on: (name, callback)->
                onEventCallbacks[name] = callback
        }
    }
)
