from abc import ABC, abstractclassmethod


class BaseInstrumentor(ABC):
    @abstractclassmethod
    def initialize(self, **kwargs):
        pass
