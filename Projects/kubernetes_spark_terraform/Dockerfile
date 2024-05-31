FROM datamechanics/spark:3.2-latest

# Run installation tasks as root
USER 0

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -\
    && apt update \
    && apt --yes upgrade

RUN snap install helm kubectl awscli --classic \\ 
    && helm repo update \\
    && helm install my-spark-operator spark-operator/spark-operator  --create-namespace --namespace spark-operator --set webhook.enable=true || true \\
    && kubectl create serviceaccount spark || true \\
    && kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default || true

WORKDIR /opt/spark/work-dir

# Official UID for spark process
ARG spark_uid=185

# Specify the user info for spark_uid
RUN useradd -d /home/sparkuser -ms /bin/bash -u ${spark_uid} sparkuser \
    && chown -R sparkuser /opt/spark/work-dir \
    && mkdir /tmp/spark-events \
    && chown -R sparkuser /tmp/spark-events

#  app dependencies and path to openjdk11
ENV APP_DIR=/opt/spark/work-dir \
    PYTHON=python3 \
    PIP=pip3

# Preinstall dependencies
COPY requirements.txt ${APP_DIR}

RUN ${PIP} install --upgrade pip \
    && ${PIP} install --no-cache-dir -r ${APP_DIR}/requirements.txt \
    && rm -f ${APP_DIR}/requirements.txt

USER ${spark_uid}

# Copy local files to image (ordered so that more likely to change is copied later)
# Python script to start the program
COPY --chown=sparkuser ./run.py ${APP_DIR}
COPY --chown=sparkuser ./runpi.py ${APP_DIR}
COPY --chown=sparkuser ./runjupyter.py ${APP_DIR}
# data will be local to image
COPY --chown=sparkuser ./data ${APP_DIR}/data
# Python code (using module name for directory)
COPY --chown=sparkuser k8spark ${APP_DIR}/k8spark

# Ensure owned by Spark
RUN chown -R sparkuser:sparkuser ${APP_DIR}/*

# https://stackoverflow.com/questions/41694329/docker-run-override-entrypoint-with-shell-script-which-accepts-arguments
# Example override for docker run: docker run --entrypoint bash -ti --rm IMAGE_NAME
# Example override for docker run: docker run --entrypoint python -p 8888:8888 --rm IMAGE_NAME runpi.py
# DO OVERRIDE entrypoint defined in datamechanics/spark when running command Docker
# DO NOT OVERRIDE entrypoint when running on kubernetes cluster (comment out)
#ENTRYPOINT ["python", "run.py"]