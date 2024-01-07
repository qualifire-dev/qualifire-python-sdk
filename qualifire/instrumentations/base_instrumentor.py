from abc import ABC, abstractclassmethod


class BaseInstrumentor(ABC):
    @abstractclassmethod  # type: ignore[arg-type]
    def initialize(self, **kwargs):
        pass
