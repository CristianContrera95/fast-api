class EntityNotFoundException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class ViewNotFoundException(EntityNotFoundException):
    def __init__(self, message="Could not find view"):
        super().__init__(message)


class ViewPermissionNotFoundException(EntityNotFoundException):
    def __init__(self, message="Could not find view permission"):
        super().__init__(message)


class RoleNotFoundException(EntityNotFoundException):
    def __init__(self, message="Could not find role"):
        super().__init__(message)


class OrganizationNotFoundException(EntityNotFoundException):
    def __init__(self, message="Could not find organization"):
        super().__init__(message)


class CloudServiceNotFoundException(EntityNotFoundException):
    def __init__(self, message="Cloud service not found"):
        super().__init__(message)
