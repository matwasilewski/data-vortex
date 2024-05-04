from pathlib import Path
from typing import List, Optional

from dagster import ConfigurableResource
from dagster_gcp import GCSResource


class ExternalResource(ConfigurableResource):
    """Base class for external resources."""

    def read(
        self, source_name: str, partition: Optional[str] = None
    ) -> List[bytes]:
        raise NotImplementedError()


class ExternalResourceOnFs(ExternalResource):
    base_dir: str

    def read(
        self, source_name: str, partition: Optional[str] = None
    ) -> List[bytes]:
        files_as_bytes = []

        if partition:
            directory_path = Path(self.base_dir) / source_name / partition
        else:
            directory_path = Path(self.base_dir) / source_name

        if not directory_path.exists():
            raise FileNotFoundError(
                f"The directory {directory_path} does not exist."
            )

        file_paths = list(directory_path.iterdir())

        for file_path in file_paths:
            if file_path.is_dir():
                raise IsADirectoryError(
                    f"The path {file_path} is a directory. Directories are not accepted in resources."
                )
            elif file_path.name.startswith("."):
                continue
            else:
                with file_path.open("rb") as file:
                    files_as_bytes.append(
                        file.read()
                    )

        return files_as_bytes

