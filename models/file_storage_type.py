from enum import Enum


class FileStorageType(str, Enum):
    Azure = "Azure"
    S3 = "S3"
    Dropbox = "Dropbox"
    Drive = "Drive"
