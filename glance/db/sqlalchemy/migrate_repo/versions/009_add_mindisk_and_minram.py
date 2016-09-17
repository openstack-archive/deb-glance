# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import *  # noqa

from glance.db.sqlalchemy.migrate_repo.schema import (
    Boolean, DateTime, Integer, String, Text)  # noqa


def get_images_table(meta):
    """
    Returns the Table object for the images table that
    corresponds to the images table definition of this version.
    """
    images = Table('images',
                   meta,
                   Column('id', Integer(), primary_key=True, nullable=False),
                   Column('name', String(255)),
                   Column('disk_format', String(20)),
                   Column('container_format', String(20)),
                   Column('size', Integer()),
                   Column('status', String(30), nullable=False),
                   Column('is_public',
                          Boolean(),
                          nullable=False,
                          default=False,
                          index=True),
                   Column('location', Text()),
                   Column('created_at', DateTime(), nullable=False),
                   Column('updated_at', DateTime()),
                   Column('deleted_at', DateTime()),
                   Column('deleted',
                          Boolean(),
                          nullable=False,
                          default=False,
                          index=True),
                   Column('checksum', String(32)),
                   Column('owner', String(255)),
                   Column('min_disk', Integer(), default=0),
                   Column('min_ram', Integer(), default=0),
                   mysql_engine='InnoDB',
                   extend_existing=True)

    return images


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    images = get_images_table(meta)

    min_disk = Column('min_disk', Integer(), default=0)
    min_disk.create(images)

    min_ram = Column('min_ram', Integer(), default=0)
    min_ram.create(images)
