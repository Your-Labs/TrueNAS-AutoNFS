#!/usr/bin/env python3

import logging
from src.TrueNAS import TrueNAS
from src.Config import Config
from time import sleep


def main():
    config = Config.new_from_env()
    logger = logging.getLogger("TrueNAS")
    logging.basicConfig(
        level=config.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    truenas = TrueNAS(
        host=config.host,
        api_key=config.api_key,
        verify_ssl=config.ssl_verify,
        dry_run=config.dry_run,
        logger=logger
    )
    try:
        while True:
            try:
                with truenas:
                    truenas.update_nfs_share(
                        parent_dataset_id=config.parent_dataset_id,
                        parent_real_path=config.parent_real_path,
                        filter_path_pattern=config.filter_path_pattern,
                        filter_path_mode=config.filter_path_mode,
                        filter_path_reversed=config.filter_path_reversed
                    )
                    logger.info(f"NFS share updated successfully for {config.parent_dataset_id}.")
            except Exception as e:
                logger.error(f"Error updating NFS share: {e}")
            logger.info(f"Sleeping for {config.check_period_sec} seconds...")
            sleep(config.check_period_sec)

    except KeyboardInterrupt:
        logger.info("Process interrupted. Exiting...")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
    finally:
        logger.info("Exiting the script.")


if __name__ == "__main__":
    main()
