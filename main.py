from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

YAML_LAYER = {
    "debug": True,
    "log_level": "info",
    "api_key": "key-h0ufgjer6q",
}

DOTENV_LAYER = {
    "api_key": "key-fi3uh2sodt",
}

OS_ENV_LAYER = {
    "workers": 6,
    "debug": True,
    "log_level": "info",
    "api_key": "key-pshcgjrmz9",
}


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


def coerce_value(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    config.update(YAML_LAYER)
    config.update(DOTENV_LAYER)
    config.update(OS_ENV_LAYER)

    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = value

    for key in list(config.keys()):
        config[key] = coerce_value(key, config[key])

    config["api_key"] = "****"

    return config