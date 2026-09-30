# DRF configuration of the kit. Import it in the service settings: `from mini_kit.settings import REST_FRAMEWORK`.
REST_FRAMEWORK = {
    # Every endpoint requires a valid token, see mini_kit.auth.authentication.
    "DEFAULT_AUTHENTICATION_CLASSES": ["mini_kit.auth.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # JSON in, JSON out.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # Every error leaves as {"error": {"code", "message"}}, see mini_kit.exception_handler.
    "EXCEPTION_HANDLER": "mini_kit.exception_handler.kit_exception_handler",
    # None instead of AnonymousUser, so the kit does not depend on django.contrib.auth.
    "UNAUTHENTICATED_USER": None,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}
