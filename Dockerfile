FROM centos/python-27-centos7

COPY requirements.txt /opt/app-root/src/
COPY app.py /opt/app-root/src/
COPY wsgi.py /opt/app-root/src/
COPY info.json /opt/app-root/src/
COPY data.csv /opt/app-root/src/

COPY s2i /opt/app-root/s2i

USER root

RUN chown -fR 1001 /opt/app-root

USER 1001

RUN rm -rf .local && \
    source scl_source enable python27 && \
    pip install --no-cache --user -r /opt/app-root/src/requirements.txt

LABEL io.k8s.description="S2I builder for spatial dataset backends." \
      io.k8s.display-name="Spatial Dataset Backend Generator" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder" \
      io.openshift.s2i.scripts-url="image:///opt/app-root/s2i/bin"

CMD [ "/opt/app-root/s2i/bin/run" ]