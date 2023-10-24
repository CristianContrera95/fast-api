import logging
import os
import uuid

from azure.storage.blob import ContainerClient

logger = logging.getLogger(__name__)


class Storage:

    """
    Azure kwargs required:
        'AZURE_KEY_STORAGE_ACCOUNT_NAME'
        'AZURE_KEY_STORAGE_ACCOUNT_KEY'
        'CONTAINER_NAME'
    AWS environments variables required:
        'AWS_ACCESS_KEY_ID'
        'AWS_SECRET_ACCESS_KEY'
        'AWS_DEFAULT_REGION'
        'AWS_BUCKET'
    """

    clouds = ["azure", "aws", "gpc"]

    def __init__(self, cloud, **kwargs):
        assert cloud in self.clouds, f"Argument cloud should be: {','.join(self.clouds)}"
        self.cloud = cloud
        if cloud == "azure":
            self.connection = self.__init_azure(**kwargs)
        elif cloud == "aws":
            self.connection = self.__init_aws(**kwargs)
        else:
            pass
            #  self.connection = self.__init_gcp(**kwargs)

    def __init_azure(self, **kwargs):
        """
        Init and azure storage account connection usign connection string

        """
        from azure.storage.blob import BlobServiceClient

        connection_string = f'DefaultEndpointsProtocol=https;AccountName={kwargs["AZURE_KEY_STORAGE_ACCOUNT_NAME"]};AccountKey={kwargs["AZURE_KEY_STORAGE_ACCOUNT_KEY"]};EndpointSuffix=core.windows.net'
        container_name = kwargs["CONTAINER_NAME"]
        blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(connection_string)
        container_client: ContainerClient = blob_service_client.get_container_client(container_name)
        return container_client

    def __init_aws(self, **kwargs):  # TODO: No probado
        """
        Init and aws s3 storage connection usign connection string
        """
        # os.makedirs('~/.aws', exist_ok=True)
        # if not os.path.exists('~/.aws/credentials'):
        #     with open('~/.aws/credentials', 'w') as fp:
        #         creds_str = f"[default] \naws_access_key_id = {kwargs['AWS_ACCESS_KEY_ID']} \naws_secret_access_key = {kwargs['AWS_SECRET_ACCESS_KEY']} \n\n"
        #         fp.write(creds_str)
        #
        # if not os.path.exists('~/.aws/config'):
        #     with open('~/.aws/config', 'w') as fp:
        #         config_str = f"[default] \nregion = {kwargs['AWS_DEFAULT_REGION']}"
        #         fp.write(config_str)

        assert (
            len({"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"}.intersection(set(os.environ))) == 3
        ), "AWS environment variables not found"
        import boto3

        s3_client = boto3.client("s3")
        bucket_client = s3_client.Bucket(os.environ["AWS_BUCKET"])
        return bucket_client

    def __get_files_azure(self, name_starts_with=None, names_only=False):
        files = self.connection.list_blobs(name_starts_with)
        if names_only:
            files = map(lambda x: x["name"], files)
        return files

    def __get_files_aws(self, name_starts_with=None, names_only=False):  # TODO: No probado
        files = self.connection.objects.filter(Prefix=name_starts_with).all()
        if names_only:
            files = map(lambda x: x.key, files)
        return files

    def get_files(self, file_name_starts=None, names_only=False):
        """Method to allow access to files data in bucket"""
        if self.cloud == "azure":
            return self.__get_files_azure(name_starts_with=file_name_starts, names_only=names_only)
        elif self.cloud == "aws":
            return self.__get_files_aws(name_starts_with=file_name_starts, names_only=names_only)

    def __download_file_azure(self, file_name):
        try:
            blob = self.connection.download_blob(file_name)
            return blob
        except Exception as ex:
            logger.error(str(ex))
            return None

    def __download_file_aws(self, file_name):  # TODO: No probado
        try:
            blob = self.connection.Object(file_name)
            return blob
        except Exception as ex:
            logger.error(str(ex))
            return None

    def download_file(self, file_name):
        """Method to download files from bucket"""
        if self.cloud == "azure":
            return self.__download_file_azure(file_name)
        elif self.cloud == "aws":
            return self.__download_file_aws(file_name)

    def __upload_file_azure(self, fp, file_name):
        blob_client = self.connection.get_blob_client(file_name)
        blob_client.upload_blob(fp, blob_type="BlockBlob")
        return f"{self.connection.url}/{file_name}"

    def __upload_file_aws(self, fp, file_name):  # TODO: No probado
        obj = self.connection.Object("file_name")
        obj.upload_fileobj(fp)
        return file_name

    def upload_file(self, fp, file_name=None, ext=""):
        """Method to upload files to bucket"""
        if file_name is None:
            # generate file_name really really unique (really)
            file_name = f"{str(uuid.uuid1())}-{str(uuid.uuid4())}.{ext}"
        else:
            file_name, ext = file_name.split(".")[:-1], file_name.split(".")[-1]
            file_name = ".".join(file_name)
            len_files = len(list(self.get_files(file_name, names_only=True)))
            if len_files > 0:
                file_name = f"{file_name}({len_files}).{ext}"

        if self.cloud == "azure":
            return self.__upload_file_azure(fp, file_name)
        elif self.cloud == "aws":
            return self.__upload_file_aws(fp, file_name)
        else:
            return None
