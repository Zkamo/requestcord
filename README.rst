requestcord
==========

.. image:: https://img.shields.io/pypi/v/requestcord.svg
   :target: https://pypi.python.org/pypi/requestcord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/requestcord.svg
   :target: https://pypi.python.org/pypi/requestcord
   :alt: PyPI supported Python versions

A modern, lightweight **Discord API wrapper for Python** focused on speed, simplicity, and clean request handling.  
RequestCord is built for developers who want direct access to Discord’s REST API without heavy abstractions or browser automation.

Key Features
-------------

- Modern Pythonic SYNC API.
- Automatically generates Discord-compatible HTTP headers
- Structured, developer-friendly return objects

Installing
----------

**Python 3.11 or higher is required**

To install the library, you can just run the following command:

.. note::

    A `Virtual Environment <https://docs.python.org/3/library/venv.html>`__ is recommended to install
    the library, especially on Linux where the system Python is externally managed and restricts which
    packages you can install on it.


.. code:: sh

    # Linux/macOS
    python3 -m pip install -U requestcord

    # Windows
    py -3 -m pip install -U requestcord


Quick Example
--------------

.. code:: py

    from src.requestcord import SyncClient, JoinGuildPayload
    
    client = SyncClient()
    
    resp = client.guilds.join(
        payload=JoinGuildPayload(
            invite_code="YOUR_INVITE_CODE",
            token="YOUR_TOKEN"
        )
    )
    
    print(resp.json())


Links
------

- `Documentation <https://requestcord.eu/>`_
- `Official Discord Server <https://discord.gg/hM5VE7XDKr>`_