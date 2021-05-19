import pychromecast
import subprocess
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(threadName)s][%(levelname)-5s] %(message)s', datefmt='%m/%d %H:%M:%S')
log = logging.getLogger('AutoTwitchCast')

stream_url = 'twitch.tv/squiffyk'
live_check_interval = 60
stream_end_sleep_interval = 60 * 60 * 8

log.info('Starting up')

while True:
    try:
        log.debug('Checking stream...')
        streams = json.loads(subprocess.check_output(['streamlink', stream_url, '--json']))
        url = streams['streams']['best']['url']
        log.info(f'Found url: {url}')

        log.info('Getting chromecast...')
        chromecasts, _ = pychromecast.get_chromecasts()
        cast = [cc for cc in chromecasts if cc.device.friendly_name == 'TV'][0]
        cast.wait()
        log.info(f'Found chromecast, status: {cast.status}')
        log.info('Playing stream...')
        mc = cast.media_controller
        mc.play_media(url, 'video/mp4')
        mc.block_until_active()
        while True:
            log.debug(f'Stream playing, sleeping for {live_check_interval} seconds...')
            time.sleep(live_check_interval)
            log.debug('Getting chromecast status...')
            mc.update_status()
            if mc.status.player_state != 'PLAYING':
                log.info(f'Stream ended, sleeping for {stream_end_sleep_interval} seconds...')
                time.sleep(stream_end_sleep_interval)
                break
    except IndexError:
        log.info('Chromecast not found')
    except pychromecast.error.UnsupportedNamespace:
        log.info(f'Chromecast changed cast, sleeping for {stream_end_sleep_interval} seconds...')
        time.sleep(stream_end_sleep_interval)
    except subprocess.CalledProcessError:
        continue
    log.debug(f'Not live, sleeping for {live_check_interval} seconds...')
    time.sleep(live_check_interval)


