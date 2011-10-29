from manygui.Exceptions import UnimplementedMethod
from manygui.Components import AbstractComponent

class AbstractGenericButton(AbstractComponent):
    #_text = "GenericButton"
    def _get_text(self):
        return self._text

    def _set_text(self, text):
        if self._text != text:
            self._text = text
            # self._ensure_text()

    def _ensure_text(self):
        raise UnimplementedMethod(self, "_ensure_text")
