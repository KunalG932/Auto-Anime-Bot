# Licensed under GNU General Public License
# Copyright (C) 2024  Dhruv-Tara

import libtorrent as lt
import time
from typing import Dict, Optional
from AAB import LOG
from pyrogram.types import Message
import os

SAVE_PATH = './downloads'
UPDATE_INTERVAL = 10  # seconds

def download_magnet(link: str, message: Message) -> Optional[Dict[str, str]]:
    """
    Download a file using a magnet link.

    Args:
    link (str): The magnet link of the file to download.
    message (Message): A Pyrogram Message object for updating download progress.

    Returns:
    Optional[Dict[str, str]]: A dictionary containing the file path and name if successful,
                              or None if an error occurs.
    """
    try:
        ses = lt.session()
        ses.listen_on(6881, 6891)
        params = {'save_path': SAVE_PATH}

        handle = lt.add_magnet_uri(ses, link, params)
        ses.start_dht()

        LOG.info('Waiting for torrent metadata...')
        while not handle.has_metadata():
            time.sleep(1)

        LOG.info(f'Starting download of {handle.name()}')

        begin = time.time()
        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            state_str = ['queued', 'checking', 'downloading metadata',
                         'downloading', 'finished', 'seeding', 'allocating']
            
            progress_msg = (f'{s.progress * 100:.2f}% complete '
                            f'(down: {s.download_rate / 1000:.1f} kB/s '
                            f'up: {s.upload_rate / 1000:.1f} kB/s '
                            f'peers: {s.num_peers}) {state_str[s.state]}')
            
            LOG.info(progress_msg)
            message.edit_text(progress_msg)
            
            time.sleep(UPDATE_INTERVAL)

        end = time.time()
        elapsed_time = end - begin
        LOG.info(f"{handle.name()} COMPLETE")
        LOG.info(f"Elapsed Time: {int(elapsed_time // 60)}min : {int(elapsed_time % 60)}sec")
        
        message.edit_text("Download complete. Preparing for upload...")
        
        file_path = os.path.join(SAVE_PATH, handle.name())
        return {"file": file_path, "name": handle.name()}

    except Exception as e:
        LOG.error(f"Error during torrent download: {e}")
        message.edit_text(f"Download failed: {str(e)}")
        return None
