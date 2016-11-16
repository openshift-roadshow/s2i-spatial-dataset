FROM centos/python-27-centos7

COPY requirements.txt /opt/app-root/src/
COPY app.py /opt/app-root/src/
COPY wsgi.py /opt/app-root/src/
COPY info.json /opt/app-root/src/
COPY data.csv /opt/app-root/src/

COPY s2i /opt/app-root/s2i

RUN rm -rf .local && \
    source scl_source enable python27 && \
    pip install --no-cache --user -r requirements.txt && \
    rm requirements.txt && \
    chown -R 1001 .local && \
    find .local -type d -exec chmod -f g+rwx,o+rx {} \; && \
    find .local -perm 2755 -exec chmod -f g+w {} \; && \
    find .local -perm 0644 -exec chmod -f g+w {} \;

LABEL io.k8s.description="S2I builder for spatial dataset backends." \
      io.k8s.display-name="Spatial Dataset Backend Generator" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder" \
      io.openshift.s2i.scripts-url="image:///opt/app-root/s2i/bin"

CMD [ "/opt/app-root/s2i/bin/run" ]
