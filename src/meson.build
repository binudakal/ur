pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'ur'

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'ur.in',
  output: 'ur',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

ur_sources = [
  '__init__.py',
  'main.py',
  'start_window.py',
  'game_window.py',
  'game_elements.py',
  'game.py',
  'scores.py',
  'settings.py',
  'main.css',
]

install_data(ur_sources, install_dir: moduledir)
