define([
    'io'
    'scripts/settings'
], (io, settings)->
    socket = new SockJS(settings.getBaseUrl())
    onEventCallbacks = {}
    socket.onmessage = (message)->
        event = JSON.parse(message)

        if event.name in onEventCallbacks
            onEventCallbacks[event.name](event.data)

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
