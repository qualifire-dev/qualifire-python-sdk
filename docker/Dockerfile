FROM python:3.11-slim-buster

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ] ; then \
      uv sync --frozen --no-cache ; \
    else \
      uv sync --frozen --no-cache --no-dev ; \
    fi

COPY . .

CMD ["/bin/bash"]
