from quart.app import *


class ThreadedApp(Quart):  # Threaded in the sense that it doesn't throw any errors...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            debug: Optional[bool] = None,
            use_reloader: bool = True,
            loop: Optional[asyncio.AbstractEventLoop] = None,
            ca_certs: Optional[str] = None,
            certfile: Optional[str] = None,
            keyfile: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        """Run this application.

        This is best used for development only, see Hypercorn for
        production servers.

        Arguments:
            host: Hostname to listen on. By default this is loopback
                only, use 0.0.0.0 to have the server listen externally.
            port: Port number to listen on.
            debug: If set enable (or disable) debug mode and debug output.
            use_reloader: Automatically reload on code changes.
            loop: Asyncio loop to create the server in, if None, take default one.
                If specified it is the caller's responsibility to close and cleanup the
                loop.
            ca_certs: Path to the SSL CA certificate file.
            certfile: Path to the SSL certificate file.
            keyfile: Path to the SSL key file.
        """
        if kwargs:
            warnings.warn(
                f"Additional arguments, {','.join(kwargs.keys())}, are not supported.\n"
                "They may be supported by Hypercorn, which is the ASGI server Quart "
                "uses by default. This method is meant for development and debugging."
            )

        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if "QUART_ENV" in os.environ:
            self.env = get_env()
            self.debug = get_debug_flag()
        elif "QUART_DEBUG" in os.environ:
            self.debug = get_debug_flag()

        if debug is not None:
            self.debug = debug

        loop.set_debug(self.debug)

        shutdown_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:
            shutdown_event.set()

        # try:
        # loop.add_signal_handler(signal.SIGTERM, _signal_handler)
        # loop.add_signal_handler(signal.SIGINT, _signal_handler)
        # except (AttributeError, NotImplementedError):
        #    pass

        server_name = self.config.get("SERVER_NAME")
        sn_host = None
        sn_port = None
        if server_name is not None:
            sn_host, _, sn_port = server_name.partition(":")

        if host is None:
            host = sn_host or "127.0.0.1"

        if port is None:
            port = int(sn_port or "5000")

        task = self.run_task(
            host,
            port,
            debug,
            use_reloader,
            ca_certs,
            certfile,
            keyfile,
            shutdown_trigger=shutdown_event.wait,  # type: ignore
        )
        print(f" * Serving Quart app '{self.name}'")  # noqa: T201
        print(f" * Environment: {self.env}")  # noqa: T201
        if self.env == "production":
            print(  # noqa: T201
                " * Please use an ASGI server (e.g. Hypercorn) directly in production"
            )
        print(f" * Debug mode: {self.debug or False}")  # noqa: T201
        scheme = "https" if certfile is not None and keyfile is not None else "http"
        print(f" * Running on {scheme}://{host}:{port} (CTRL + C to quit)")  # noqa: T201

        try:
            loop.run_until_complete(task)
        finally:
            try:
                _cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                asyncio.set_event_loop(None)
                loop.close()


def _cancel_all_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    if not tasks:
        return

    for task in tasks:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    for task in tasks:
        if not task.cancelled() and task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )
