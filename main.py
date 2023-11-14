import json

import here.geotiles.heretile as heretile
from here.geotiles.heretile import BoundingBox, GeoCoordinate
from here.platform import Platform

from download_options import FileFormat, HerePlatformCatalog
from hmc_tile_downloader import HmcTileDownloader

if __name__ == '__main__':
    ### Customized configurations
    # home_path = os.path.expanduser(os.getenv('USERPROFILE'))
    # platform_cred = PlatformCredentials.from_credentials_file(os.path.join(home_path, '.here', 'credentials.properties'))
    # platform_obj = Platform(platform_cred)
    # platform = Platform(credentials=platform_cred, environment=Environment.DEFAULT)

    ### Platform SDK initialization
    platform = Platform()
    env = platform.environment
    config = platform.platform_config
    print('HERE Platform Status: ', platform.get_status())

    ### Query by Lat/Lng or Tile/Partition LONGKEY ID

    south_west = (9.591465308256108, 97.73522936323553)
    north_east = (20.981253503936394, 106.08727704044883)

    download_center = GeoCoordinate(lng=8.41036, lat=49.00839)
    download_bounding_box = BoundingBox(west=south_west[1], south=south_west[0], east=north_east[1], north=north_east[0])
    download_tile_id_list = [23599607]

    search_input = download_bounding_box

    ### Catalog selection
    catalog = HerePlatformCatalog.RIB2

    ### List of HERE Tile/Partition ID
    here_quad_longkey_list = []

    ### Download Layers (Empty: all layers)
    layers = ['electric-vehicle-charging-stations']

    ### Main runner

    level: int
    hrn: str

    if catalog == HerePlatformCatalog.RIB2:
        hrn = 'hrn:here:data::olp-here:rib-2'
        level = 12
    elif catalog == HerePlatformCatalog.HDLM:
        hrn = 'hrn:here:data::olp-here-had:here-hdlm-protobuf-weu-2'
        level = 14

    if isinstance(search_input, GeoCoordinate):
        here_quad_longkey_list = [heretile.from_coordinates(search_input.lng, search_input.lat, level)]
    elif isinstance(search_input, BoundingBox):
        here_quad_longkey_list = list(heretile.in_bounding_box(search_input.west, search_input.south, search_input.east,
                                                               search_input.north, level))
    elif isinstance(search_input, list):
        here_quad_longkey_list = download_tile_id_list

    if len(here_quad_longkey_list) == 0:
        print('No tile/partition ID presented, quit.')
    else:
        catalog = platform.get_catalog(hrn=hrn)
        catalog_detail = json.loads(json.dumps(catalog.get_details()))
        catalog_layers = catalog_detail['layers']
        print('Available layers: ')
        for catalog_layer in catalog_layers:
            print('\t', catalog_layer['id'])
        if len(layers) == 0:
            for catalog_layer in catalog_layers:
                if catalog_layer['partitioningScheme'] == 'heretile':
                    layers.append(catalog_layer['id'])
        print('download layers:', layers)
        for layer in layers:
            HmcTileDownloader(catalog=catalog, layer=layer, tile_ids=here_quad_longkey_list,
                              file_format=FileFormat.JSON).download()
