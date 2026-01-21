"""Centralized HTTP and SSL configuration utilities.

This module consolidates all SSL certificate verification, HTTP library patching,
and progress bar suppression into a single location to reduce code duplication
and improve maintainability.
"""

import os
import ssl
import sys
import warnings
from typing import Callable
from functools import wraps
from unittest.mock import MagicMock


def configure_http_environment() -> None:
    """Configure HTTP environment variables and disable SSL verification.

    This should be called BEFORE importing any HTTP libraries (requests, httpx, urllib3)
    and BEFORE importing akshare.
    """
    # Disable tqdm progress bars globally
    os.environ['TQDM_DISABLE'] = '1'
    os.environ['SSL_VERIFY'] = 'false'

    # Disable SSL certificate verification environment variables
    ssl_env_vars = {
        'REQUESTS_CA_BUNDLE': '',
        'CURL_CA_BUNDLE': '',
        'SSL_CERT_FILE': '',
        'SSL_CERT_DIR': '',
        'PYTHONHTTPSVERIFY': '0',
        'REQUESTS_INSECURE_SSL': '1',
    }

    for var, value in ssl_env_vars.items():
        os.environ[var] = value


def suppress_ssl_warnings() -> None:
    """Suppress SSL/HTTPS verification warnings from urllib3 and Python warnings."""
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        pass

    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    warnings.filterwarnings('ignore', category=DeprecationWarning)


def suppress_tqdm_progress_bars() -> None:
    """Monkey-patch tqdm to disable progress bars before akshare imports it.

    This creates a no-op tqdm class and injects it into sys.modules before
    akshare attempts to import tqdm, preventing progress bar output.
    """
    class NoOpTqdm:
        """No-operation tqdm replacement that silently ignores progress updates."""

        def __init__(self, *args, **kwargs):
            self.iterable = args[0] if args else []
            self.n = 0
            self.total = kwargs.get('total', len(self.iterable) if hasattr(self.iterable, '__len__') else None)

        def __iter__(self):
            return iter(self.iterable)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def update(self, n=1):
            self.n += n

        def close(self):
            pass

        def set_description(self, desc):
            pass

        @staticmethod
        def disable(flag):
            pass

    try:
        sys.modules['tqdm.std'] = MagicMock()
        sys.modules['tqdm.std'].tqdm = NoOpTqdm
        sys.modules['tqdm.auto'] = MagicMock()
        sys.modules['tqdm.auto'].tqdm = NoOpTqdm
        sys.modules['tqdm'] = MagicMock()
        sys.modules['tqdm'].tqdm = NoOpTqdm
    except Exception:
        # Silently ignore if tqdm patching fails
        pass


def configure_ssl_context() -> ssl.SSLContext:
    """Configure and return a default SSL context with verification disabled.

    Returns:
        ssl.SSLContext: Configured SSL context with hostname checking and
                       certificate verification disabled.
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    return ssl_context


def patch_ssl_globally(ssl_context: ssl.SSLContext) -> None:
    """Apply SSL context patches globally to stdlib and third-party libraries.

    Args:
        ssl_context: The SSL context to use for patching.
    """
    # Patch stdlib SSL module
    ssl._create_default_https_context = lambda: ssl_context
    ssl._create_unverified_context = lambda: ssl_context

    # Try to patch the low-level _ssl module
    try:
        import _ssl
        if hasattr(_ssl, 'SSLContext'):
            _ssl.SSLContext.check_hostname = False
            _ssl.SSLContext.verify_mode = ssl.CERT_NONE
    except Exception:
        pass


def patch_urllib3() -> None:
    """Patch urllib3 to disable SSL verification by default."""
    try:
        import urllib3
        original_init = urllib3.PoolManager.__init__

        def patched_init(self, *args, **kwargs):
            kwargs['cert_reqs'] = 'CERT_NONE'
            # assert_hostname was removed in newer urllib3 versions, so remove it if present
            kwargs.pop('assert_hostname', None)
            return original_init(self, *args, **kwargs)

        urllib3.PoolManager.__init__ = patched_init
    except Exception:
        pass


def patch_requests() -> None:
    """Patch requests library to disable SSL verification by default."""
    try:
        import requests
        original_request = requests.Session.request

        def patched_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return original_request(self, method, url, **kwargs)

        requests.Session.request = patched_request
    except Exception:
        pass


def patch_httpx() -> None:
    """Patch httpx library to disable SSL verification by default."""
    try:
        import httpx

        # Patch synchronous client
        original_init = httpx.Client.__init__
        def patched_init(self, *args, **kwargs):
            kwargs.setdefault('verify', False)
            return original_init(self, *args, **kwargs)
        httpx.Client.__init__ = patched_init

        # Patch async client
        original_async_init = httpx.AsyncClient.__init__
        def patched_async_init(self, *args, **kwargs):
            kwargs.setdefault('verify', False)
            return original_async_init(self, *args, **kwargs)
        httpx.AsyncClient.__init__ = patched_async_init
    except ImportError:
        pass


def configure_all() -> None:
    """Apply all HTTP and SSL configurations in the correct order.

    This should be called as early as possible, preferably at module import time,
    BEFORE importing akshare or any HTTP libraries.

    Call order matters:
    1. Environment variables must be set first
    2. tqdm must be mocked before akshare imports it
    3. SSL context must be configured
    4. Library patches must be applied
    5. Warnings must be suppressed
    """
    configure_http_environment()
    suppress_tqdm_progress_bars()

    ssl_context = configure_ssl_context()
    patch_ssl_globally(ssl_context)

    patch_urllib3()
    patch_requests()
    patch_httpx()

    suppress_ssl_warnings()
