from app.languages.en import en
from app.languages.tr import tr

lang = {}
lang["en"] = en
lang["tr"] = tr


def _(request, string, *args):
    keys = string.split(".")
    lang_dict = lang.get(request.ctx.language, lang.get("en", {}))
    for key in keys:
        if key not in lang_dict:
            return key
        lang_dict = lang_dict[key]
    return lang_dict.format(*args) if args else lang_dict
