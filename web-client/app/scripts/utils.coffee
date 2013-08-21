define({
    serialize: (obj)->
        str = []
        for key, value of obj
            str.push(encodeURIComponent(key) + "=" + encodeURIComponent(value))

        return str.join("&")
})
