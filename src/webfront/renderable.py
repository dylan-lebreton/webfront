from abc import ABC, abstractmethod

from typeguard import typechecked


@typechecked
class Renderable(ABC):
    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.render()

    def __str__(self) -> str:
        return self.render()
