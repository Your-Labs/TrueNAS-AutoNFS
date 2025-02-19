# autonfs Service

This project provides a containerized `autonfs` service for managing NFS shares in **TrueNAS**. It helps automate the process of checking and updating TrueNAS NFS shares by using a variety of configuration options set through environment variables.

## Requirements

- **Docker** and **Docker Compose** should be installed on your machine.
- **TrueNAS server**: You should have a running TrueNAS server to interact with.

## Environment Variables

The `autonfs` container uses the following environment variables to configure how it interacts with **TrueNAS**:

| Variable                         | Description                                                                 | Default Value           |
|----------------------------------|-----------------------------------------------------------------------------|-------------------------|
| `TRUENAS_HOST`                   | The TrueNAS server's address (IP or domain)                                 |                         |
| `TRUENAS_API_KEY_FILE`           | Path to the TrueNAS API key file                                            |                         |
| `TRUENAS_API_KEY`                | The TrueNAS API key (if not using a file)                                    |                         |
| `TRUENAS_PARENT_DATASET_ID`      | The parent dataset ID in TrueNAS                                            | `data/home`             |
| `TRUENAS_PARENT_REAL_PATH`       | The real path to the parent dataset in TrueNAS                               | `/mnt`                  |
| `TRUENAS_SSL_VERIFY`             | Whether to verify SSL certificates (True/False)                              | `True`                  |
| `TRUENAS_CHECK_PERIOD_SEC`       | The period (in seconds) to check the NFS share                               | `600`                   |
| `TRUENAS_DRY_RUN`                | Whether to perform a dry run (True/False)                                    | `False`                 |
| `TRUENAS_FILTER_PATH_MODE`       | Path filter mode (can be `start_with`, `end_with`, `contains`, `regex`)      | `end_with`              |
| `TRUENAS_FILTER_PATH_PATTERN`    | The pattern to use for filtering paths (string or regex)                     | `_`                     |
| `TRUENAS_FILTER_PATH_REVERSED`   | Whether to reverse the path filter logic (True/False)                        | `True`                  |
| `TRUENAS_LOG_LEVEL`              | The log level (can be `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)       | `INFO`                  |
| `TRUENAS_NFS_COMMON_NETWORK`     | The network range (e.g., `192.168.1.0/24`) for common NFS shares             |                         |
| `TRUENAS_NFS_COMMON_HOSTS`       | Comma-separated list of allowed hosts for the NFS share                      |                         |
| `TRUENAS_NFS_AUTO_REMOVE`        | Whether to automatically remove NFS shares (True/False) while the dataset not exist                       | `True`                  |
