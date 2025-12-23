from . import sync_api
from .sync_api.client import SyncClient
from .sync_api import *

__all__ = (
    "SyncClient",
    *sync_api.__all__,
)

__version__ = "2.0.0"
__author__ = "Zkamo, VatosV2"
