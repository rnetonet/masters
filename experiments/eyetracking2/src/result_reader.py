class ResultReader:
    """Reads a result file of a high dataset into an array of integers (0 or 1)."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.result = None

    def read(self):
        """Reads the file an returns an array of 0 / 1."""
        if not self.result:
            file_handle = open(self.file_path)
            file_content = file_handle.read()
            file_content_splitted = file_content.split()

            self.result = list(map(int, file_content_splitted))

        return self.result
