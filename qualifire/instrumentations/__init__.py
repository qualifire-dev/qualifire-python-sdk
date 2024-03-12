from importlib.metadata import version

from . import base_instrumentor


def is_openai_v1():
    try:
        version = version("openai") >= "1.0.0"
        return version
    except:
        return None


if is_openai_v1() is True:
    from .openai.v1.openai_instrumentor import OpenAiInstrumentorV1

    instrumentors = [OpenAiInstrumentorV1]
elif is_openai_v1() is False:
    from .openai.v0.openai_instrumentor import OpenAiInstrumentorV0

    instrumentors = [OpenAiInstrumentorV0]
else:
    instrumentors = []
