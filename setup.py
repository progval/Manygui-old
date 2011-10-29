from distutils.core import setup

setup (name               = 'manygui',
       version            = open('VERSION.txt').read().strip(),
       maintainer         = 'Valentin Lorentz',
       maintainer_email   = 'progval@gmail.co!',
       description        = 'Generic GUI Package for Python',
       long_description   = 'Generic GUI Package for Python',
       license            = 'MIT License',
       url                = 'https://github.com/ProgVal/Manygui',
       platforms          = ['Any'],
       package_dir        = {'': 'lib'},
       packages           = ['manygui', 'manygui.backends',
                              'manygui.backends.txtutils'])
