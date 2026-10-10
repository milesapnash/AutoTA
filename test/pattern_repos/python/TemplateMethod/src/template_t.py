from abc import ABC, abstractmethod


class TemplateT(ABC):
    def do_something(self):
        self.do_something_first()
        self.do_something_second()

    @abstractmethod
    def do_something_first(self):
        pass

    @abstractmethod
    def do_something_second(self):
        pass
