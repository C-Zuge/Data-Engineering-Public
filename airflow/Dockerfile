FROM apache/airflow:2.4.3-python3.9

USER root

# Airflow
ARG AIRFLOW_USER_HOME=/opt/airflow
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV AIRFLOW_VERSION="2.5.0"
ENV AIRFLOW_UID=1000
ENV ACCEPT_EULA=Y
ENV GUNICORN_CMD_ARGS--log-level ERROR
ENV PATH="${PATH}:${AIRFLOW_HOME}/ext_modules"
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}/ext_modules"


RUN set -ex \
    && buildDeps=' \
        libpq-dev \
        libpq5 \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
	build-essential \
        python-dev \
        python3-dev \
        g++ \
        gcc \
        libc-dev \
        libffi-dev \
        git \
        libsasl2-2 \
        libsasl2-modules-gssapi-mit \
    ' \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install msodbcsql17 -y \
    && apt-get install -y --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        vim \
        curl \
        rsync \
        netcat \
    && apt-get purge --auto-remove -y $buildDeps \
    && apt-get autoremove -y --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base


COPY ./airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

RUN chown -R airflow: ${AIRFLOW_USER_HOME}

RUN chmod -R 777 ${AIRFLOW_USER_HOME}

USER airflow

COPY ./requirements.txt .


RUN pip install -U pip setuptools wheel && \
    pip install --upgrade pip  && \
    pip install psycopg2-binary && \
    pip install apache-airflow && \
    pip install --no-cache-dir -r ./requirements.txt \
    pip install -U pyopenssl
