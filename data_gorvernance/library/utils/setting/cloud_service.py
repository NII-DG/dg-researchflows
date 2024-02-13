import os
from pathlib import Path

from ..file import JsonFile

# cloud-service.jsonのファイルパス
json_path = Path(os.path.dirname(__file__)).joinpath('../../data/cloud-service.json').resolve()


class CloudService:
    __FIELD = 'cloud_service'
    __ID = 'id'
    __NAME = 'service_name'
    __DESCRIPTION = 'description'
    __PATH = 'path'
    __IS_ACTIVE = 'is_active'

    def __init__(self):
        contents = JsonFile(str(json_path)).read()
        self.cloud_services = contents[self.__FIELD]

    def get_names(self):
        return [cloud_service[self.__NAME] for cloud_service in self.cloud_services]

    def get_disabled_names(self):
        disabled = []
        for cloud_service in self.cloud_services:
            if not cloud_service[self.__IS_ACTIVE]:
                disabled.append(cloud_service[self.__NAME])
        return disabled

    def get_id(self, name):
        cloud_service = self.__get_cloud_service(name)
        if not cloud_service:
            return None
        return cloud_service[self.__ID]

    def get_path(self, name):
        cloud_service = self.__get_cloud_service(name)
        if not cloud_service:
            return None
        return cloud_service[self.__PATH]

    def get_description(self, name):
        cloud_service = self.__get_cloud_service(name)
        if not cloud_service:
            return None
        return cloud_service[self.__DESCRIPTION]

    def __get_cloud_service(self, name):
        for cloud_service in self.cloud_services:
            if cloud_service[self.__NAME] == name:
                return cloud_service
