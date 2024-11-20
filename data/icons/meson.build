application_id = 'com.github.binudakal.ur'

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)

# Install other SVGs in symbolic directory
sym_dir = 'hicolor' / 'symbolic'

install_data(
  sym_dir / 'white_counter.svg',
  sym_dir / 'black_counter.svg',
  sym_dir / 'dice.svg',
  sym_dir / 'rosette.svg',
  sym_dir / '1-3-11.svg',
  sym_dir / '2-6-9-12.svg',
  sym_dir / '7-10.svg',
  sym_dir / '5.svg',
  sym_dir / '13.svg',

  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)
