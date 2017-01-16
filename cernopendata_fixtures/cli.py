# -*- coding: utf-8 -*-
#
# This file is part of CERN Open Data Portal.
# Copyright (C) 2017 CERN.
#
# CERN Open Data Portal is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# CERN Open Data Portal is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Command line interface for CERN Open Data Portal."""

from __future__ import absolute_import, print_function

import glob
import os

import click
import pkg_resources
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.orm.attributes import flag_modified


@click.group(chain=True)
def fixtures():
    """Automate site bootstrap process and testing."""


@fixtures.command()
@with_appcontext
def collections():
    """Load default collections."""
    from invenio_db import db
    from invenio_collections.models import Collection

    from .fixtures import COLLECTIONS

    def load(collections, parent=None):
        """Create new collection."""
        for data in collections or []:
            collection = Collection(
                name=data['name'], dbquery=data.get('dbquery'),
                parent=parent
            )
            db.session.add(collection)
            db.session.flush()
            load(data.get('children'), parent=collection)

    load(COLLECTIONS)
    db.session.commit()


@fixtures.command()
@with_appcontext
def records():
    """Load demo records."""
    from dojson.contrib.marc21.utils import load
    from dojson.contrib.marc21.model import marc21
    from invenio_db import db
    from invenio_records import Record

    data = pkg_resources.resource_filename('cernopendata_fixtures', 'data')
    files = list(glob.glob(os.path.join(data, '*.xml')))
    files += list(glob.glob(os.path.join(data, '*', '*.xml')))

    for filename in files:
        with open(filename, 'rb') as source:
            for record in load(source):
                click.echo(Record.create(record).id)
    db.session.commit()


@fixtures.command()
@with_appcontext
def pids():
    """Fetch and register PIDs."""
    from invenio_db import db
    from invenio_oaiserver.fetchers import oaiid_fetcher
    from invenio_oaiserver.minters import oaiid_minter
    from invenio_pidstore.errors import PIDDoesNotExistError, \
        PersistentIdentifierError
    from invenio_pidstore.models import PIDStatus, PersistentIdentifier
    from invenio_pidstore.fetchers import recid_fetcher
    from invenio_pidstore.minters import recid_minter
    from invenio_records.models import RecordMetadata

    with click.progressbar(RecordMetadata.query.all()) as bar:
        for record in bar:
            try:
                pid = recid_fetcher(record.id, record.json)
                found = PersistentIdentifier.get(
                    pid_type=pid.pid_type,
                    pid_value=pid.pid_value,
                    pid_provider=pid.provider.pid_provider
                )
                click.echo('Found {0}.'.format(found))
            except PIDDoesNotExistError:
                db.session.add(
                    PersistentIdentifier.create(
                        pid.pid_type, pid.pid_value,
                        object_type='rec', object_uuid=record.id,
                        status=PIDStatus.REGISTERED
                    )
                )
            except KeyError:
                click.echo('Skiped: {0}'.format(record.id))
                continue

            pid_value = record.json.get('_oai', {}).get('id')
            if pid_value is None:
                assert 'control_number' in record.json
                pid_value = current_app.config.get(
                    'OAISERVER_ID_PREFIX'
                ) + str(record.json['control_number'])

                record.json.setdefault('_oai', {})
                record.json['_oai']['id'] = pid.pid_value

            pid = oaiid_fetcher(record.id, record.json)
            try:
                found = PersistentIdentifier.get(
                    pid_type=pid.pid_type,
                    pid_value=pid.pid_value,
                    pid_provider=pid.provider.pid_provider
                )
                click.echo('Found {0}.'.format(found))
            except PIDDoesNotExistError:
                pid = oaiid_minter(record.id, record.json)
                db.session.add(pid)

            flag_modified(record, 'json')
            assert record.json['_oai']['id']
            db.session.add(record)

    db.session.commit()
