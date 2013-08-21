import tornadio2


def event(name_or_func):
    if callable(name_or_func) and len(name_or_func.__name__.split('_')) > 1:
        return tornadio2.event(':'.join(name_or_func.__name__.split('_')))(name_or_func)

    return tornadio2.event(name_or_func)
