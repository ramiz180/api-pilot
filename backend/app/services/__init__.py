"""Services package — business-logic layer.

Public exception
----------------
SpecImportError
    Raised by the import service when a spec cannot be fetched, parsed,
    or persisted.  Named ``SpecImportError`` (not ``ImportError``) to avoid
    shadowing Python's built-in ``ImportError`` for module imports.
"""


class SpecImportError(Exception):
    """Raised when a spec import fails for any reason.

    Possible causes:
    - Workspace does not exist
    - HTTP fetch failure (for URL imports)
    - Spec content cannot be parsed as Swagger / OpenAPI
    - Database write failure
    """
