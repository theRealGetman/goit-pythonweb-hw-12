.. Contact Book documentation master file, created by
   sphinx-quickstart on Thu Apr 10 18:39:31 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Contact Book API Documentation
===============================

This documentation covers the Contact Book API, a FastAPI application for managing contacts.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

Main Application
=================
.. automodule:: main
  :members:
  :undoc-members:
  :show-inheritance:

Configuration
==============
.. automodule:: src.config.config
  :members:
  :undoc-members:
  :show-inheritance:

Database Models
================

Base Model
-----------
.. automodule:: src.db.models.base
  :members:
  :undoc-members:
  :show-inheritance:

User Model
-----------
.. automodule:: src.db.models.user
  :members:
  :undoc-members:
  :show-inheritance:

Contact Model
-------------
.. automodule:: src.db.models.contact
  :members:
  :undoc-members:
  :show-inheritance:

Database Connection
-------------------
.. automodule:: src.db.db
  :members:
  :undoc-members:
  :show-inheritance:

API Routes
==========

Authentication Routes
---------------------
.. automodule:: src.api.auth
  :members:
  :undoc-members:
  :show-inheritance:

Contact Routes
--------------
.. automodule:: src.api.contacts
  :members:
  :undoc-members:
  :show-inheritance:

User Routes
-----------
.. automodule:: src.api.users
  :members:
  :undoc-members:
  :show-inheritance:

Utility Routes
--------------
.. automodule:: src.api.utils
  :members:
  :undoc-members:
  :show-inheritance:

Services
========

Authentication Service
----------------------
.. automodule:: src.services.auth
  :members:
  :undoc-members:
  :show-inheritance:

User Service
------------
.. automodule:: src.services.user
  :members:
  :undoc-members:
  :show-inheritance:

Contact Service
---------------
.. automodule:: src.services.contacts
  :members:
  :undoc-members:
  :show-inheritance:

File Upload Service
-------------------
.. automodule:: src.services.upload_file
  :members:
  :undoc-members:
  :show-inheritance:

Repositories
============

User Repository
---------------
.. automodule:: src.repository.user
  :members:
  :undoc-members:
  :show-inheritance:

Contact Repository
------------------
.. automodule:: src.repository.contacts
  :members:
  :undoc-members:
  :show-inheritance:

Schemas
========

User Schemas
-------------
.. automodule:: src.schemas.user
  :members:
  :undoc-members:
  :show-inheritance:

Contact Schemas
----------------
.. automodule:: src.schemas.contact
  :members:
  :undoc-members:
  :show-inheritance:

Token Schemas
--------------
.. automodule:: src.schemas.token
  :members:
  :undoc-members:
  :show-inheritance:

Indices and tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

