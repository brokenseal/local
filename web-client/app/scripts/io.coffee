define([
    'io'
    'scripts/settings'
], (io, settings)->
    return {
        chat: io.connect(settings.getBaseUrl() + 'chat')
    }
)
