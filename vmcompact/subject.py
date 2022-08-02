class Subject:
    """Adds support for observers"""

    def __init__(self):
        """list of current observers"""

        self._observers = list()

    def notify(self, modifier=None):
        """run callbacks on update"""

        [o.on_update(modifier) for o in self._observers]

    def add(self, observer):
        """adds an observer to _observers"""

        if observer not in self._observers:
            self._observers.append(observer)

    def remove(self, observer):
        """removes an observer from _observers"""

        if observer in self._observers:
            self._observers.remove(observer)

    def get(self) -> list:
        """returns the current _observers"""

        return self._observers

    def clear(self):
        """clears the _observers list"""

        self._observers.clear()
