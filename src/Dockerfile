FROM registry.access.redhat.com/ubi8/python-38:1-27

USER root
ENV TZ=utc \
    NLS_LANG=AMERICAN_AMERICA.UTF8 \
    PATH="${PATH}:/app"

RUN mkdir -p /app/resources/ && \
    chmod -R 755 /app/ && \
    chown -R 1001:1001 /app/

COPY ./resources/* /app/resources/

RUN python${PYTHON_VERSION} -m pip install --no-cache-dir \
    -r /app/resources/requirements.txt

COPY ./scripts/* /app/

USER 1001

CMD ["/bin/env","python${PYTHON_VERSION}","/app/rcurl-probe.py"]