import os
from EasySetting import Config

cfg = Config(cfg_path=os.path.join(
    os.path.dirname(__file__),
    'cfg.ini'
))

data_folder = os.path.join(
    os.environ.get('SYNC', None),
    'Material in Standard Chinese')

cfg.add(os.path.join(data_folder, 'pinYin Table.json'),
        'pinYinTable',
        'Path')

cfg.add(os.path.join(data_folder, 'ciZu Table.json'),
        'ciZuTable',
        'Path')

cfg.save()
