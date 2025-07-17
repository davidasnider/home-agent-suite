# This __init__.py file serves two main purposes for the package:
#
# 1.  It signals to Python that the `tomorrow_io_client` directory should be
#     treated as a package, allowing modules within it to be imported.
#
# 2.  It defines the public API of the package. By importing key classes or
#     functions here (like `TomorrowIoTool`), we make them directly accessible
#     to consumers. This allows for cleaner imports, such as:
#
#         from tomorrow_io_client import TomorrowIoTool
#
#     Instead of the more verbose and implementation-specific:
#
#         from tomorrow_io_client.client import TomorrowIoTool

from .client import TomorrowIoTool

__all__ = ["TomorrowIoTool"]