from __future__ import annotations
from dataclasses import dataclass, field
import json
import ssl
import http.client
import urllib.parse
import logging
import re

class ErrNotConnected(Exception):
    def __init__(self, msg: str = "Not connected to TrueNAS"):
        super().__init__(msg)


def filter_str(string: str, pattern: str, mode: str = 'start_with', reversed: bool = False) -> bool:
    """
    Filter the string by pattern
    Args:
        string: The string to filter
        pattern: The pattern to filter
        mode: The filter mode,can be 'start_with', 'end_with', 'contains', 'regex', default is 'start_with'
        reversed: If True, return the opposite result, default is False
    Returns:
        bool
    """
    if mode == 'start_with':
        match = string.startswith(pattern)
    elif mode == 'end_with':
        match = string.endswith(pattern)
    elif mode == 'contains':
        match = pattern in string
    elif mode == 'regex':
        match = re.search(pattern, string) is not None
    else:
        match = True
    return match if not reversed else not match


@dataclass
class _base:

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def from_json(self, json_str: str):
        self.__dict__ = json.loads(json_str)

    def from_dict(self, dict_data: dict):
        for key, value in self.__dict__.items():
            if key in dict_data:
                self.__dict__[key] = dict_data[key]

    @classmethod
    def new_from_json(cls, json_str: str) -> _base:
        obj = cls()
        obj.from_json(json_str)
        return obj

    @classmethod
    def new_from_dict(cls, dict_data: dict) -> _base:
        obj = cls()
        obj.from_dict(dict_data)
        return obj


@dataclass
class DataSet(_base):
    """
    Represents a Dataset
    """
    id: int = field(default=None)
    type: str = field(default=None)
    name: str = field(default=None)
    pool: str = field(default=None)
    encrypted: bool = field(default=False)
    encryption_root: str = field(default=None)
    key_loaded: bool = field(default=False)
    children: list = field(default_factory=list)

    def from_dict(self, dict_data: dict):
        super().from_dict(dict_data)
        raise NotImplementedError("Please use new_from_dict")

    def __super_from_dict(self, dict_data: dict):
        super().from_dict(dict_data)

    def from_json(self, json_str: str):
        raise NotImplementedError("Please use new_from_json")

    @classmethod
    def new_from_json(cls, json_str: str) -> DataSet:
        data_dict = json.loads(json_str)
        return cls.new_from_dict(data_dict)

    @classmethod
    def new_from_dict(cls, dict_data: dict) -> DataSet:
        obj = cls()
        obj.__super_from_dict(dict_data)
        children_list: list[DataSet] = []
        for child in dict_data["children"]:
            if isinstance(child, dict):
                child_obj = DataSet.new_from_dict(child)
                children_list.append(child_obj)
            elif isinstance(child, DataSet):
                children_list.append(child)
        obj.children = children_list
        return obj


@dataclass
class DataSetDict():
    """
    Represents a list of Datasets
    """
    data: dict = field(default_factory=dict)

    def __iter__(self):
        return iter(self.data.values())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key) -> DataSet:
        return self.data[key]

    def __setitem__(self, key, value: DataSet):
        self.update(value)

    def add(self, dataset: DataSet | list[DataSet]):
        if isinstance(dataset, list) and len(dataset) > 0 and isinstance(dataset[0], DataSet):
            for ds in dataset:
                if ds.id in self.data:
                    print(f"Duplicate ID {ds.id}, skipping")
                    continue
                self.data[ds.id] = ds
        elif isinstance(dataset, DataSet):
            id = dataset.id
            if id in self.data:
                print(f"Duplicate ID {id}, skipping")
                return
            self.data[id] = dataset
        else:
            raise Exception("Invalid type, expected DataSet or list[DataSet]")

    def update(self, dataset: DataSet | list[DataSet]):
        if isinstance(dataset, list) and len(dataset) > 0 and isinstance(dataset[0], DataSet):
            for ds in dataset:
                self.data[ds.id] = ds
        elif isinstance(dataset, DataSet):
            self.data[dataset.id] = dataset
        else:
            raise Exception("Invalid type, expected DataSet or list[DataSet]")

    def get(self, id: int) -> DataSet:
        if id not in self.data:
            raise Exception(f"ID {id} not found")
        return self.data[id]

    def keys(self) -> set[str]:
        return self.data.keys()

    def values(self) -> list[DataSet]:
        return self.data.values()


@dataclass
class NfsShareAdd(_base):
    """
    Represents a NFS Share to be added
    """
    path: str = field(default=None)
    aliases: list = field(default_factory=list)
    networks: list = field(default_factory=list)
    hosts: list = field(default_factory=list)


@dataclass
class NfsShare(NfsShareAdd):
    """
    Represents a NFS Share
    """
    id: int = field(default=None)
    # path: str = field(default=None)
    # aliases: list = field(default_factory=list)
    comment: str = field(default=None)
    # hosts: list = field(default_factory=list)
    ro: bool = field(default=False)
    maproot_user: str = field(default=None)
    maproot_group: str = field(default=None)
    mapall_user: str = field(default=None)
    mapall_group: str = field(default=None)
    security: list = field(default_factory=list)
    enabled: bool = field(default=False)
    # networks: list = field(default_factory=list)
    locked: bool = field(default=False)

    @classmethod
    def new_from_json(cls, json_str) -> NfsShare:
        return super().new_from_json(json_str)


@dataclass
class NfsShareDict(_base):
    """
    Represents a list of NFS Shares
    """
    data: dict[str, NfsShare] = field(default_factory=dict)

    def __iter__(self):
        return iter(self.data.values())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key) -> NfsShare:
        return self.data[key]

    def __setitem__(self, key, value: NfsShare):
        self.update(value)

    def add(self, nfs_share: NfsShare):
        id = nfs_share.path
        if id in self.data:
            raise Exception(f"Duplicate ID {id}")
        self.data[id] = nfs_share

    def update(self, nfs_share: NfsShare):
        if not isinstance(nfs_share, NfsShare):
            raise Exception("Invalid type")
        self.data[nfs_share.path] = nfs_share

    def get(self, path: str | list[str]) -> NfsShare | list[NfsShare]:
        """
        Get the NFS Share by path.

        Args:
            path: The path of the NFS Share to get. It can be a string or a list of strings.

        Returns:
            NfsShare | list[NfsShare]: If path is a string, return the NFS Share; 
                                    if path is a list, return a list of NFS Shares (if not found, return None).
        """
        if isinstance(path, list):
            return [self.data.get(p, None) for p in path]
        if path not in self.data:
            raise Exception(f"ID {path} not found")
        return self.data[path]

    def filter_by_path(self, path: str, mode: str = 'start_with') -> NfsShare:
        new_dict = NfsShareDict()
        for nfs_share in self.data.values():
            if filter_str(nfs_share.path, path, mode):
                new_dict.update(nfs_share)
        return new_dict

    def keys(self) -> set[str]:
        return self.data.keys()

    def values(self) -> list[NfsShare]:
        return self.data.values()

    @classmethod
    def new_from_json(cls, json_str: str) -> NfsShareDict:
        dictData = json.loads(json_str)
        obj = cls()
        for nfs_dict in dictData:
            nfs_share = NfsShare.new_from_dict(nfs_dict)
            obj.update(nfs_share)
        return obj


class TrueNAS:

    @dataclass
    class NfsModify:
        add: list = field(default_factory=list)
        remove: list = field(default_factory=list)

        def filter(self, pattern: str, mode: str = 'start_with', reversed: bool = False):
            """
            Filter the list by pattern
            Args:
                pattern: The pattern to filter
                mode: The filter mode, default is 'start_with'
            Returns:
                list
            """
            self.add = [item for item in self.add if filter_str(string=item, pattern=pattern, mode=mode, reversed=reversed)]
            self.remove = [item for item in self.remove if filter_str(string=item, pattern=pattern, mode=mode, reversed=reversed)]

    def __init__(self,
                 host: str,
                 api_key: str,
                 prefix: str = "/api/v2.0",
                 verify_ssl: bool = True,
                 dry_run: bool = False,
                 logger: logging.Logger = None
                 ):
        self.__conn: http.client.HTTPSConnection = None
        self.host = host
        self.api_key = api_key
        self.prefix = prefix
        self.verify_ssl = verify_ssl
        self.dry_run = dry_run
        if logger is not None and isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        if self.is_connected:
            self.close()

    @property
    def conn(self) -> http.client.HTTPSConnection:
        return self.__conn

    @property
    def is_connected(self) -> bool:
        return self.__conn is not None

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # "Accept": "application/json"
            "Accept": "*/*"
        }

    def connect(self) -> http.client.HTTPSConnection:
        if self.is_connected:
            self.logger.info("Already connected")
            return self.__conn
        if not self.verify_ssl:
            self.logger.info(f"Connecting to https://{self.host} without SSL verification")
            context = ssl._create_unverified_context()
            self.__conn = http.client.HTTPSConnection(self.host, context=context)
        else:
            self.logger.info(f"Connecting to https://{self.host}")
            self.__conn = http.client.HTTPSConnection(self.host)
        return self.__conn

    def close(self):
        if not self.is_connected:
            self.logger.info("Already disconnected")
            return
        self.logger.info("Closing connection")
        self.__conn.close()
        self.__conn = None

    def format_request_path(self, path: str) -> str:
        """
        Formats the request path to include the prefix.
        If the path does not start with /api, it will be added {prefix}/{path}
        """
        if not path.startswith("/api"):
            if path.startswith("/"):
                path = path[1:]
            return f"{self.prefix}/{path}"
        return path

    def _validate_connection(self):
        if not self.is_connected:
            raise ErrNotConnected()

    def _validate_response(self, res: http.client.HTTPResponse):
        if res.status != 200:
            raise Exception(f"Request failed with status {res.status}")

    def get(self, path: str, params: dict = None) -> str:
        """
        Request a GET to the TrueNAS API
        """
        self._validate_connection()
        path = self.format_request_path(path)
        if params:
            query_string = urllib.parse.urlencode(params)
            path = f"{path}?{query_string}"
        self.conn.request("GET", path, headers=self.headers)
        res = self.conn.getresponse()
        self._validate_response(res)
        data = res.read().decode()
        return data

    def post(self, path: str, data: str) -> str:
        """
        Request a POST to the TrueNAS API
        """
        self._validate_connection()
        path = self.format_request_path(path)
        if self.dry_run:
            self.logger.info(f"dry_run: POST - {path} - {data}")
            return ""
        self.conn.request("POST", path, data, headers=self.headers)
        res = self.conn.getresponse()
        self._validate_response(res)
        data = res.read().decode()
        return data

    def delete(self, path: str) -> str:
        """
        Request a DELETE to the TrueNAS API
        """
        self._validate_connection()
        path = self.format_request_path(path)
        if self.dry_run:
            self.logger.info(f"dry_run: DELETE - {path}")
        self.conn.request("DELETE", path, headers=self.headers)
        res = self.conn.getresponse()
        self._validate_response(res)
        data = res.read().decode()
        return data

    def add_nfs_share(self, nfs_share: NfsShareAdd) -> NfsShare:
        """
        Add a NFS Share
        Args:
            nfs_share: The NFS Share to add
        Returns:
            NfsShare
        """
        data = nfs_share.to_json()
        data = self.post("/sharing/nfs", data)
        return NfsShare.new_from_json(data)

    def delete_nfs_share(self, id: str | int) -> str:
        """
        Delete a NFS Share
        Args:
            id: The ID of the NFS Share to delete
        Returns:
            str
        """
        if isinstance(id, int):
            id = str(id)
        elif not isinstance(id, str):
            id = str(int(id))
        else:
            raise Exception("Invalid ID, it must be a string or an integer")
        return self.delete(f"/sharing/nfs/id/{id}")

    def get_nfs_share(self, id: str = None) -> NfsShare | NfsShareDict:
        """
        Get a NFS Share configuration
        Args:
            id: The ID of the NFS Share to get; if None, all NFS Shares will be returned
        Returns:
            NfsShare | NfsShareDict
        """
        all = False
        if id is not None and id != "":
            path = f"/sharing/nfs/{id}"
        else:
            path = "/sharing/nfs"
            all = True
        data = self.get(path)
        if all:
            return NfsShareDict.new_from_json(data)
        else:
            return NfsShare.new_from_json(data)

    def get_nfs_share_id_by_path(self, path: str | list[str]) -> str | list[str]:
        """
        Get the NFS Share ID by path
        Args:
        """
        nfs_shares: NfsShareDict = self.get_nfs_share()
        print(nfs_shares)
        nfs_share_list = nfs_shares.get(path)
        print(nfs_share_list)
        if isinstance(path, list):
            return [nfs_share.id for nfs_share in nfs_share_list if nfs_share is not None]
        return nfs_share_list.id

    def get_dataset(self, id: str = None, params: dict = None) -> DataSet:
        """
        Get a Dataset configuration
        Args:
            id: The ID of the Dataset to get, if None, all Datasets will be returned
        Returns:
            DataSet
        """
        if id is not None and id != "":
            id_encoded = urllib.parse.quote(id, safe="")
            path = f"/pool/dataset/id/{id_encoded}"
        else:
            path = "/pool/dataset"
        if params is not None:
            params["extra.retrieve_children"] = "true"
        data = self.get(path=path, params=params)
        return DataSet.new_from_json(data)

    def compare_nfs_with_personal_dataset(self, parent_dataset_id: str, parent_real_path: str = "/mnt") -> TrueNAS.NfsModify:
        """
        compare the NFS shares with the personal dataset
        Args:
            parent_dataset_id: The parent dataset id
            parent_real_path: The parent real path, default is "/mnt"
        """
        datasets = self.get_dataset(parent_dataset_id)
        dataset_dict = DataSetDict()
        dataset_dict.update(datasets.children)
        nfs_shares: NfsShareDict = self.get_nfs_share()
        nfs_shares = nfs_shares.filter_by_path(f"{parent_real_path}/{parent_dataset_id}", mode='start_with')
        nfs_shares_keys = nfs_shares.keys()
        dataset_keys = dataset_dict.keys()
        dataset_keys = set([f"{parent_real_path}/{key}" for key in dataset_keys])
        not_in_nfs = list(dataset_keys - nfs_shares_keys)
        not_in_dataset = list(nfs_shares_keys - dataset_keys)
        nfs_modify = TrueNAS.NfsModify(add=not_in_nfs, remove=not_in_dataset)
        return nfs_modify

    def update_nfs_share(self, parent_dataset_id: str,
                         parent_real_path: str = "/mnt",
                         common_config: NfsShareAdd = None,
                         filter_path_pattern: str = "_",
                         filter_path_mode: str = "end_with",
                         filter_path_reversed: bool = True,
                         remove: bool = True) -> TrueNAS.NfsModify:
        nfs_modify = self.compare_nfs_with_personal_dataset(parent_dataset_id=parent_dataset_id, parent_real_path=parent_real_path)
        nfs_modify.filter(pattern=filter_path_pattern, mode=filter_path_mode, reversed=filter_path_reversed)
        if remove and len(nfs_modify.remove) > 0:
            self.logger.info("Removing NFS Shares")
            for path in nfs_modify.remove:
                try:
                    self.delete_nfs_share(path)
                    self.logger.info(f"Removed {path}")
                except Exception as e:
                    self.logger.info(f"Failed to remove {path}: {e}")
        if len(nfs_modify.add) == 0:
            return
        self.logger.info("Adding NFS Shares")
        nfs_share = common_config
        if nfs_share is None or not isinstance(nfs_share, NfsShareAdd):
            nfs_share = NfsShareAdd()
        for path in nfs_modify.add:
            try:
                nfs_share = NfsShareAdd(path=path)
                self.add_nfs_share(nfs_share)
                self.logger.info(f"Added {path}")
            except Exception as e:
                self.logger.info(f"Failed to add {path}: {e}")
