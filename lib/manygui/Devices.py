
''' Devices classes for Manygui.

    Valentin Lorentz 2011
'''

__all__ = '''

    Mouse
    Keyboard

'''.split()

class BaseDevice:
    pass

class Mouse(BaseDevice):
    def __repr__(self):
        return 'manygui.Devices.Mouse()'

class Keyboard(BaseDevice):
    def __repr__(self):
        return 'manygui.Devices.Keyboard()'
