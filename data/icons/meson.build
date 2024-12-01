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

# Install counter and dice SVGs in symbolic directory
sym_dir = 'hicolor' / 'symbolic'

install_data(
  sym_dir / 'white_counter.svg',
  sym_dir / 'black_counter.svg',
  sym_dir / 'dice.svg',

  install_dir: get_option('datadir') / 'icons' / sym_dir
)

# Install tile SVGs in symbolic directory
tile_dir = 'hicolor' / 'symbolic' / 'tiles'

install_data(
  tile_dir / 'rosette.svg',
  tile_dir / '1-3-11.svg',
  tile_dir / '2-6-9-12.svg',
  tile_dir / '7-10.svg',
  tile_dir / '5.svg',
  tile_dir / '13.svg',
  tile_dir / '15.svg',
  tile_dir / 'empty.svg',

  install_dir: get_option('datadir') / 'icons' / tile_dir
)