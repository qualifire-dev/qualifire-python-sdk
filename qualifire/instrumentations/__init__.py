from importlib.metadata import version

from . import base_instrumentor
from .openai.v0.openai_instrumentor import OpenAiInstrumentorV0
from .openai.v1.openai_instrumentor import OpenAiInstrumentorV1


def is_openai_v1():
    return version("openai") >= "1.0.0"


if is_openai_v1():
    instrumentors = [OpenAiInstrumentorV0]
else:
    instrumentors = [OpenAiInstrumentorV1]
