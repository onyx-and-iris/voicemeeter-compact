class Subject:
    """Adds support for observers"""

    def __init__(self):
        """list of current observers"""

        self._observers = list()

    def notify(self, modifier=None):
        """run callbacks on update"""

        [o.on_update(modifier) for o in self._observers]

    def add(self, observer):
        """adds an observer to observables"""

        if observer not in self._observers:
            self._observers.append(observer)

    def remove(self, observer):
        """removes an observer from observables"""

        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def get(self) -> list:
        """returns the current observables"""

        return self._observers

    def clear(self):
        """clears the observables list"""

        self._observers.clear()
