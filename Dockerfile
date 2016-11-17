FROM centos/python-27-centos7

COPY wsgi.py /opt/app-root/

COPY info.json /opt/app-root/src/
COPY data.csv /opt/app-root/src/

COPY s2i /opt/app-root/s2i

USER root

RUN source scl_source enable python27 && \
    virtualenv /opt/app-root && \
    source /opt/app-root/bin/activate && \
    pip install --no-cache mod_wsgi Flask flask-restful pymongo && \
    chmod -Rf g+w /opt/app-root

ENV PATH=/opt/app-root/bin:$PATH

USER 1001

LABEL io.k8s.description="S2I builder for spatial dataset backends." \
      io.k8s.display-name="Spatial Dataset Backend Generator" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder" \
      io.openshift.s2i.scripts-url="image:///opt/app-root/s2i/bin"

CMD [ "/opt/app-root/s2i/bin/run" ]
