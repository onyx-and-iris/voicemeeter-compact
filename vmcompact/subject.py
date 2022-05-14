class Subject:
    def __init__(self):
        """list of current observers"""

        self._observables = []

    def notify(self, modifier=None):
        """run callbacks on update"""

        for observer in self._observables:
            observer.on_update()

    def add(self, observer):
        """adds an observer to observables"""

        if observer not in self._observables:
            self._observables.append(observer)

    def remove(self, observer):
        """removes an observer from observables"""

        try:
            self._observables.remove(observer)
        except ValueError:
            pass

    def get(self) -> list:
        """returns the current observables"""

        return self._observables

    def clear(self):
        """clears the observables list"""

        self._observables.clear()
