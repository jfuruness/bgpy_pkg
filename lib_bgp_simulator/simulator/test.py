class Test:
    def __init__(self, trial=None, engine=None):
        self.trial = trial
        self.engine = engine

    def run(self):
        # Run engine
        self.engine.run()
        self._collect_data()
        # delete engine from attrs so that garbage collector can come
        engine = self.engine
        del self.engine
        # Return engine so that propogation can run again
        return engine

    def _collect_data(self):
        """Collects data about the test run before engine is deleted"""

        pass
