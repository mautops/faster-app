MIDDLEWARES = [
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "kwargs": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        },
    },
    {
        "class": "fastapi.middleware.trustedhost.TrustedHostMiddleware",
        "kwargs": {
            "allowed_hosts": ["*"],
        },
    },
]
