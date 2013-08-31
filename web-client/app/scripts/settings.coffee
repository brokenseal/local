define([], ->
    return {
        getBaseUrl: ->
            if location.hostname == 'localhost'
                return 'http://localhost:7000/'

            return 'http://local-agora.herokuapp.com/'
    }
)
