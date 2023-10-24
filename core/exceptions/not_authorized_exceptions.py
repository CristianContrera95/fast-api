class NotAuthorizedException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class NotAuthorizedViewException(NotAuthorizedException):
    def __init__(self, message="The account's role is not allowed to read this view"):
        super().__init__(message)
