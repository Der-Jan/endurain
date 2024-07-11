import logging

from typing import Annotated, Callable

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

import activity_streams.schema as activity_streams_schema
import activity_streams.crud as activity_streams_crud
import activity_streams.dependencies as activity_streams_dependencies

import activities.dependencies as activities_dependencies

import session.security as session_security

import database

#from dependencies import (
#    dependencies_security,
#)

# Define the API router
router = APIRouter()

# Define a loggger created on main.py
logger = logging.getLogger("myLogger")


@router.get(
    "/activity_id/{activity_id}/all",
    response_model=list[activity_streams_schema.ActivityStreams] | None,
)
async def read_activities_streams_for_activity_all(
    activity_id: int,
    validate_id: Annotated[
        Callable, Depends(activities_dependencies.validate_activity_id)
    ],
    check_scopes: Annotated[
        Callable, Security(session_security.check_scopes, scopes=["activities:read"])
    ],
    db: Annotated[
        Session,
        Depends(database.get_db),
    ],
):
    # Get the activity streams from the database and return them
    return activity_streams_crud.get_activity_streams(activity_id, db)


@router.get(
    "/activity_id/{activity_id}/stream_type/{stream_type}",
    response_model=activity_streams_schema.ActivityStreams | None,
)
async def read_activities_streams_for_activity_stream_type(
    activity_id: int,
    validate_activity_id: Annotated[
        Callable, Depends(activities_dependencies.validate_activity_id)
    ],
    stream_type: int,
    validate_activity_stream_type: Annotated[
        Callable, Depends(activity_streams_dependencies.validate_activity_stream_type)
    ],
    check_scopes: Annotated[
        Callable, Security(session_security.check_scopes, scopes=["activities:read"])
    ],
    db: Annotated[
        Session,
        Depends(database.get_db),
    ],
):
    # Get the activity stream from the database and return them
    return activity_streams_crud.get_activity_stream_by_type(
        activity_id, stream_type, db
    )
