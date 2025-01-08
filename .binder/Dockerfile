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
RUN apt-get install fontconfig
RUN apt-get install -y fonts-ipafont

# install vault
RUN apt-get update -y
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

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

USER ${NB_USER}

# install the notebook package etc.
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache notebook
RUN pip install --no-cache lxml==4.7.1
RUN pip install --no-cache -U nbformat==5.2.0
RUN pip install --no-cache black==21.12b0
RUN pip install --no-cache boto3
RUN pip install --no-cache chardet==4.0.0
RUN pip install --no-cache panel==1.3.0
RUN pip install --no-cache python-magic==0.4.27
RUN pip install --no-cache natsort==8.3.1
RUN pip install --no-cache pandas==2.1.4
RUN pip install --no-cache cookiecutter==2.5.0
RUN pip install --no-cache hvac==2.1.0
RUN pip install --no-cache gitpython==3.1.43
RUN pip install --no-cache git+https://github.com/RCOSDP/rdmclient.git@d9d2b7926ecdf53aede026e6c70b271f0d7b41c7
RUN pip install --no-cache git+https://github.com/NII-DG/nii-dg.git@230419_8c684da
RUN pip install --no-cache git+https://github.com/NII-DG/dg-packager.git@master
RUN pip install --no-cache graphviz==0.20.1

# TODO: リリース時にブランチを最新のタグに変更する
RUN pip install --no-cache git+https://github.com/NII-DG/dg-metadata-manager.git@3670dc0bacdb5e00501b88e126a10c52657e9355

# TODO: リリース時にはdg-drawerのブランチを変更する(@Rel20230929のようにする)
RUN pip install --no-cache git+https://github.com/NII-DG/dg-drawer.git@develop/Rel_V2.0

RUN pip install --no-cache jupyter_contrib_nbextensions
RUN jupyter contrib nbextension install --user
RUN jupyter nbextensions_configurator enable --user
RUN jupyter nbextension enable codefolding/main

# TODO: リリース時にはdg_Jupyter-LC_run_throughのタグを変更する(@Rel20230929のようにする)
RUN pip install --no-cache git+https://github.com/NII-DG/dg_Jupyter-LC_run_through.git@20240909
RUN jupyter run-through quick-setup --user

RUN pip install --no-cache git+https://github.com/NII-DG/dg_Jupyter-multi_outputs.git@master
RUN jupyter nbextension install --py lc_multi_outputs --user
RUN jupyter nbextension enable --py lc_multi_outputs --user

# TODO: リリース時にはdg-nb-extensionsのタグを変更する(@Rel20230929のようにする)
RUN pip install --no-cache git+https://github.com/NII-DG/dg-nb-extensions.git@2024-07-04
RUN jupyter nbextension install --py dg_nb_extensions --user
RUN jupyter nbextension enable --py dg_nb_extensions --user

# upgrade nbclassic ( after nbextension installed )
RUN pip install --no-cache nbclassic==0.4.8

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

# library path
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
