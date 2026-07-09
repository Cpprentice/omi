"""Transformation Module for OMI to convert to and from OEMetadata"""


import io
from pathlib import Path


class TransformationError(Exception):
    """Raised when a transformation produces an error"""


def transform_metadata(input_data_file_path: Path, output_stream: io.IO, crosswalk_file_path: Path):
    """Main function to perform transformation between different metadata standards.

    Parameters
    ----------
    input_data_file_path: pathlib.Path
        Source Metadata
    output_stream: io.IO
        Results are written here
    crosswalk_file_path: pathlib.Path
        Contains instructions to convert input to output
    """

    # TODO checking input data version against schema version in the crosswalk would be useful
