# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

FROM ghcr.io/anaticulae/baw:384399f-test

COPY requirements.dev /var/install/requirements.dev
RUN pip install -vvv -r /var/install/requirements.dev
RUN baw sync all

COPY . /var/install

WORKDIR /var/install
RUN pip install -e .

WORKDIR /var/workdir

ENTRYPOINT ["sh", "-c"]
