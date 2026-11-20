FROM ghcr.io/astral-sh/uv:0.13.6 AS uv
FROM python:3.12.16-slim-bookworm
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    XDG_DATA_HOME=/tmp/data \
    XDG_CACHE_HOME=/tmp/cache
WORKDIR /app
COPY . /app
# Optional public CA bundle for managed TLS proxies; never disable verification.
RUN --mount=type=secret,id=build_ca \
    if [ -f /run/secrets/build_ca ]; then \
      export SSL_CERT_FILE=/run/secrets/build_ca UV_SYSTEM_CERTS=true; \
    fi; \
    uv sync --locked --no-editable && uv pip check && chmod -R a+rX /app
USER 65532:65532
WORKDIR /tmp
ENTRYPOINT ["/app/.venv/bin/scopeshift"]
CMD ["demo", "--output", "/tmp/demo"]
