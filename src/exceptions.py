class DownloadError(RuntimeError):
    def __init__(self, resource):
        super().__init__(f'Could not download resource: {resource}')
