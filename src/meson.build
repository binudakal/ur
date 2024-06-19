pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'gnome_ur'
gnome = import('gnome')

gnome.compile_resources('gnome-ur',
  'gnome-ur.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'gnome-ur.in',
  output: 'gnome-ur',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

gnome_ur_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'game.py',
  'main.css'
]

install_data(gnome_ur_sources, install_dir: moduledir)
