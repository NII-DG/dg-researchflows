FROM jupyter/scipy-notebook:ubuntu-20.04

USER root
RUN apt-get clean

RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update -y
RUN apt-get install -y netbase
RUN apt-get install -y graphviz
RUN apt-get install -y libmagic1
RUN apt-get install -y iputils-ping net-tools
RUN apt-get install -y expect
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y git-annex
RUN apt-get install fontconfig
RUN apt-get install -y fonts-ipafont

# install vault
RUN apt-get install -y gpg wget lsb-release
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
RUN apt-get update -y
RUN apt-get install -y vault
RUN setcap -r /usr/bin/vault

# install ansible
RUN apt-get install -y software-properties-common
RUN apt-add-repository -y -u ppa:ansible/ansible
RUN apt-get install -y ansible

######
ENV NODE_VERSION=20.5.0

#RUN /bin/sh -c ARCH= && dpkgArch="$(dpkg --print-architecture)" && case "${dpkgArch##*-}" in amd64) ARCH='x64';; ppc64el) ARCH='ppc64le';; s390x) ARCH='s390x';; arm64) ARCH='arm64';; armhf) ARCH='armv7l';; i386) ARCH='x86';; *) echo "unsupported architecture"; exit 1 ;; esac && set -ex && apt-get update && apt-get install -y ca-certificates curl wget gnupg dirmngr xz-utils libatomic1 --no-install-recommends && rm -rf /var/lib/apt/lists/* && for key in 4ED778F539E3634C779C87C6D7062848A1AB005C 141F07595B7B3FFE74309A937405533BE57C7D57 74F12602B6F1C4E913FAA37AD3A89613643B6201 DD792F5973C6DE52C432CBDAC77ABFA00DDBF2B7 61FC681DFB92A079F1685E77973F295594EC4689 8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 890C08DB8579162FEE0DF9DB8BEAB4DFCF555EF4 C82FA3AE1CBEDC6BE46B9360C43CEC45C17AB93C 108F52B48DB57BB0CC439B2997B01419BD92F80A ; do gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" || gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key" ; done && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$ARCH.tar.xz" && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" && gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc && grep " node-v$NODE_VERSION-linux-$ARCH.tar.xz\$" SHASUMS256.txt | sha256sum -c - && tar -xJf "node-v$NODE_VERSION-linux-$ARCH.tar.xz" -C /usr/local --strip-components=1 --no-same-owner && rm "node-v$NODE_VERSION-linux-$ARCH.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt && apt-mark auto '.*' > /dev/null && find /usr/local -type f -executable -exec ldd '{}' ';' | awk '/=>/ { so = $(NF-1); if (index(so, "/usr/local/") == 1) { next }; gsub("^/(usr/)?", "", so); print so }' | sort -u | xargs -r dpkg-query --search | cut -d: -f1 | sort -u | xargs -r apt-mark manual && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && ln -s /usr/local/bin/node /usr/local/bin/nodejs && node --version && npm --version


RUN /bin/sh -c ARCH= && dpkgArch="$(dpkg --print-architecture)" && case "${dpkgArch##*-}" in amd64) ARCH='x64';; ppc64el) ARCH='ppc64le';; s390x) ARCH='s390x';; arm64) ARCH='arm64';; armhf) ARCH='armv7l';; i386) ARCH='x86';; *) echo "unsupported architecture"; exit 1 ;; esac && set -ex && apt-get update && apt-get install -y ca-certificates curl wget gnupg dirmngr xz-utils libatomic1 --no-install-recommends && rm -rf /var/lib/apt/lists/* && for key in 4ED778F539E3634C779C87C6D7062848A1AB005C 141F07595B7B3FFE74309A937405533BE57C7D57 74F12602B6F1C4E913FAA37AD3A89613643B6201 DD792F5973C6DE52C432CBDAC77ABFA00DDBF2B7 61FC681DFB92A079F1685E77973F295594EC4689 8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 890C08DB8579162FEE0DF9DB8BEAB4DFCF555EF4 C82FA3AE1CBEDC6BE46B9360C43CEC45C17AB93C 108F52B48DB57BB0CC439B2997B01419BD92F80A ; do gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" || gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key" ; done && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$ARCH.tar.xz" && curl -fsSLO --compressed "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" && gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc && grep " node-v$NODE_VERSION-linux-$ARCH.tar.xz\$" SHASUMS256.txt | sha256sum -c - && tar -xJf "node-v$NODE_VERSION-linux-$ARCH.tar.xz" -C /usr/local --strip-components=1 --no-same-owner && rm "node-v$NODE_VERSION-linux-$ARCH.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt && apt-mark auto '.*' > /dev/null && find /usr/local -type f -executable -exec ldd '{}' ';' | awk '/=>/ { so = $(NF-1); if (index(so, "/usr/local/") == 1) { next }; gsub("^/(usr/)?", "", so); print so }' | sort -u | xargs -r dpkg-query --search | cut -d: -f1 | sort -u | xargs -r apt-mark manual && apt-mark manual sudo && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && ln -s /usr/local/bin/node /usr/local/bin/nodejs && node --version && npm --version


ENV YARN_VERSION=1.22.19

RUN /bin/sh -c set -ex && savedAptMark="$(apt-mark showmanual)" && apt-get update && apt-get install -y ca-certificates curl wget gnupg dirmngr --no-install-recommends && rm -rf /var/lib/apt/lists/* && for key in 6A010C5166006599AA17F08146C2130DFD2497F5 ; do gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" || gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key" ; done && curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz" && curl -fsSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz.asc" && gpg --batch --verify yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz && mkdir -p /opt && tar -xzf yarn-v$YARN_VERSION.tar.gz -C /opt/ && ln -s /opt/yarn-v$YARN_VERSION/bin/yarn /usr/local/bin/yarn && ln -s /opt/yarn-v$YARN_VERSION/bin/yarnpkg /usr/local/bin/yarnpkg && rm yarn-v$YARN_VERSION.tar.gz.asc yarn-v$YARN_VERSION.tar.gz && apt-mark auto '.*' > /dev/null && { [ -z "$savedAptMark" ] || apt-mark manual $savedAptMark > /dev/null; } && find /usr/local -type f -executable -exec ldd '{}' ';' | awk '/=>/ { so = $(NF-1); if (index(so, "/usr/local/") == 1) { next }; gsub("^/(usr/)?", "", so); print so }' | sort -u | xargs -r dpkg-query --search | cut -d: -f1 | sort -u | xargs -r apt-mark manual && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && yarn --version

RUN apt update && \
    apt install -y --no-install-recommends \
    curl \
    jq \
    tini && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["tini", "--"]

#####

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

USER ${NB_USER}

# install the notebook package etc.
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache notebook
RUN pip install --no-cache datalad==0.17.6
RUN pip install --no-cache lxml==4.7.1
RUN pip install --no-cache blockdiag==3.0.0
RUN pip install --no-cache -U nbformat==5.2.0
RUN pip install --no-cache black==21.12b0
RUN pip install --no-cache snakemake
RUN pip install --no-cache boto3
RUN pip install --no-cache chardet==4.0.0
RUN pip install --no-cache panel==1.3.0
RUN pip install --no-cache python-magic==0.4.27
RUN pip install --no-cache natsort==8.3.1
RUN pip install --no-cache pandas==2.1.4
RUN pip install --no-cache cookiecutter==2.5.0
RUN pip install --no-cache hvac==2.1.0
RUN pip install --no-cache git+https://github.com/RCOSDP/rdmclient.git@master
RUN pip install --no-cache git+https://github.com/NII-DG/nii-dg.git@230419_8c684da
RUN pip install --no-cache git+https://github.com/NII-DG/dg-packager.git@master
# TODO: リリース時にはdg-drawerのブランチを変更する(@Rel20230929のようにする)
RUN pip install --no-cache git+https://github.com/NII-DG/dg-drawer.git@develop/Rel_V2.0

RUN pip install --no-cache jupyter_contrib_nbextensions
RUN jupyter contrib nbextension install --user
RUN jupyter nbextensions_configurator enable --user
RUN jupyter nbextension enable codefolding/main

# TODO: リリース時にはdg_Jupyter-LC_run_throughのブランチを変更する(@Rel20230929のようにする)
RUN pip install --no-cache git+https://github.com/NII-DG/dg_Jupyter-LC_run_through.git@20240216
RUN jupyter run-through quick-setup --user

RUN pip install --no-cache git+https://github.com/NII-DG/dg_Jupyter-multi_outputs.git@master
RUN jupyter nbextension install --py lc_multi_outputs --user
RUN jupyter nbextension enable --py lc_multi_outputs --user

RUN pip install --no-cache git+https://github.com/NII-DG/dg-nb-extensions.git@master
RUN jupyter nbextension install --py dg_nb_extensions --user
RUN jupyter nbextension enable --py dg_nb_extensions --user

# upgrade nbclassic ( after nbextension installed )
RUN pip install --no-cache nbclassic==0.4.8

# install Japanese-font (for blockdiag)
ARG font_deb=fonts-ipafont-gothic_00303-18ubuntu1_all.deb
RUN mkdir ${HOME}/.fonts
RUN wget -P ${HOME}/.fonts http://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-ipafont/${font_deb}
RUN dpkg-deb -x ${HOME}/.fonts/${font_deb} ~/.fonts
RUN cp ~/.fonts/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf ~/.fonts/ipag.ttf
RUN rm ${HOME}/.fonts/${font_deb}
RUN rm -rf ${HOME}/.fonts/etc ${HOME}/.fonts/usr
RUN rm .wget-hsts

# install vcpsdk
RUN wget https://s3-ap-northeast-1.amazonaws.com/vcp-jupyternotebook/23.11.0/jupyternotebook_vcpsdk-23.11.0.tgz
RUN mkdir -p ~/data_gorvernance/library/vcp
RUN tar zxvf jupyternotebook_vcpsdk-23.11.0.tgz -C ~/data_gorvernance/library/vcp/
RUN rm jupyternotebook_vcpsdk-23.11.0.tgz
RUN pip install --no-cache vrplib==1.3.0
ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/data_gorvernance/library/vcp/vcpsdk"

ARG NB_USER=jovyan
ARG NB_UID=1000

RUN rm -rf ${HOME}/work

# prepare datalad procedure dir
RUN mkdir -p ${HOME}/.config/datalad/procedures

ENV PYTHONPATH "${PYTHONPATH}:${HOME}/data_gorvernance"

WORKDIR ${HOME}
COPY . ${HOME}

USER root
RUN chown -R ${NB_UID} ${HOME}


##### User Custom Area [Start] ######
# Dockerfileを編集する場合は、「User Custom Area」内に記述してください。
# それ以外のエリアでの記述、また変数名：NB_USERの値は書き換えないでください。リサーチフロー機能が正常に働かなくなる可能性があります。
# root権限で実行したい場合は、"USER root"を、一般ユーザ権限で実行したい場合は、 "USER ${NB_USER}"を実行したいコマンド前に記述してください。




###### User Custom Area [End] #######

USER ${NB_USER}
# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
