# Expedition routes for listing and filtering expeditions
from fastapi import APIRouter
from database import read_from_database
from services.expedition_service import expedition_from_row

router = APIRouter(prefix="/expeditions")


@router.get("/")
def get_expeditions():
    results = read_from_database(
        "SELECT * FROM expedition ORDER BY name COLLATE NOCASE ASC",
        ()
    )

    expedition_list = [expedition_from_row(row) for row in results]

    return {
        "number_of_expeditions": len(expedition_list),
        "expeditions": expedition_list
    }


@router.get("/leader/{leader_id}")
def get_expeditions_by_leader(leader_id: int):
    results = read_from_database(
        """
        SELECT *
        FROM expedition
        WHERE leader_id = ?
        ORDER BY name COLLATE NOCASE ASC
        """,
        (leader_id,)
    )

    expedition_list = [expedition_from_row(row) for row in results]

    return {
        "number_of_expeditions": len(expedition_list),
        "expeditions": expedition_list
    }


@router.get("/participant/{participant_id}")
def get_expeditions_by_participant(participant_id: int):
    results = read_from_database(
        """
        SELECT expedition.*
        FROM expedition
        JOIN explorer_expedition
            ON expedition.id = explorer_expedition.expedition_id
        WHERE explorer_expedition.explorer_id = ?
        ORDER BY expedition.name COLLATE NOCASE ASC
        """,
        (participant_id,)
    )

    expedition_list = [expedition_from_row(row) for row in results]

    return {
        "number_of_expeditions": len(expedition_list),
        "expeditions": expedition_list
    }


@router.get("/discovery/{discovery_id}")
def get_expeditions_by_discovery(discovery_id: int):
    results = read_from_database(
        """
        SELECT expedition.*
        FROM expedition
        JOIN discovery
            ON expedition.id = discovery.expedition_id
        WHERE discovery.id = ?
        ORDER BY expedition.name COLLATE NOCASE ASC
        """,
        (discovery_id,)
    )

    expedition_list = [expedition_from_row(row) for row in results]

    return {
        "number_of_expeditions": len(expedition_list),
        "expeditions": expedition_list
    }