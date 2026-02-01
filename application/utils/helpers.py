from markupsafe import Markup
from flask import request

def wants_json() -> bool:
    return "application/json" in (request.headers.get("Accept", "") or "").lower()

class DummyField:
    def __init__(self, name, ftype="text", value=""):
        self.name = name; self.type = ftype; self.value = value
    def __call__(self, **kwargs):
        attrs = {"type": self.type, "name": self.name, "id": kwargs.pop("id", self.name), "value": kwargs.pop("value", self.value), **kwargs}
        parts = []
        for k,v in attrs.items():
            if v is None or v is False: continue
            parts.append(k.replace("_","-") if v is True else f'{k.replace("_","-")}="{v}"')
        return Markup(f"<input {' '.join(parts)}>")

class DummyForm:
    def __init__(self):
        self.email    = DummyField("email","email")
        self.password = DummyField("password","password")
        self.name     = DummyField("name","text")
        self.role     = DummyField("role","hidden")
    def hidden_tag(self): return Markup("")
