import logging

from .instrumentations import instrumentors

logger = logging.getLogger("qualifire")


class Client:
    def __init__(
        self,
        base_url,
        api_key,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def initialize(self):
        for instrumentor_class in instrumentors:
            logger.debug(
                "initializing instrumentor",
                {
                    "instrumentor": instrumentor_class.__name__,
                },
            )
            try:
                instrumentor = instrumentor_class(
                    api_key=self._api_key,
                    base_url=self._base_url,
                )

                instrumentor.initialize()
            except Exception:
                logger.exception("error while initializing instrumentor.")

        logger.debug("initialized all instrumentors")
