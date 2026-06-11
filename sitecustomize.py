import os
import ssl

try:
    import certifi
except ImportError:
    certifi = None


if certifi is not None:
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

    _original_create_default_context = ssl.create_default_context

    def _create_certifi_context(purpose=ssl.Purpose.SERVER_AUTH, *, cafile=None, capath=None, cadata=None):
        if cafile or capath or cadata:
            return _original_create_default_context(
                purpose=purpose,
                cafile=cafile,
                capath=capath,
                cadata=cadata,
            )

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile=certifi.where())
        return context

    ssl.create_default_context = _create_certifi_context
