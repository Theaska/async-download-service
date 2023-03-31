import argparse

parser = argparse.ArgumentParser(
    prog='ZIP photos',
    description='aiohttp server wih zipping files'
)


def parse_bool(value):
    value = str(value)
    return True if value.lower() == 'true' or value == '1' else False


parser.add_argument('--enable_logging', default=1, type=parse_bool, dest='enable_logging',)
parser.add_argument('--enable_delay', default=0, type=parse_bool, dest='enable_delay')
parser.add_argument('--photos_dir', default='test_photos', type=str, dest='photos_dir')
parser.add_argument('--batch_size', default=5*1024, type=int, dest='batch_size')

args, _ = parser.parse_known_args()