"""
Gemini Spark — Multi-Source Discovery Module Registry
"""

from .jsearch import query_jsearch
from .remotive import query_remotive
from .jobicy import query_jobicy
from .himalayas import query_himalayas
from .remote_companies import query_remote_companies_directory
from .ats_scrapers import query_public_ats_feeds

SOURCES_REGISTRY = [
    {
        "name": "RapidAPI JSearch",
        "type": "aggregator_api",
        "runner": query_jsearch,
        "enabled": True
    },
    {
        "name": "Remotive API",
        "type": "job_board_api",
        "runner": query_remotive,
        "enabled": True
    },
    {
        "name": "Jobicy API",
        "type": "job_board_api",
        "runner": query_jobicy,
        "enabled": True
    },
    {
        "name": "Himalayas API",
        "type": "job_board_api",
        "runner": query_himalayas,
        "enabled": True
    },
    {
        "name": "Remote Jobs Directory (PDF Companies)",
        "type": "company_ats_directory",
        "runner": query_remote_companies_directory,
        "enabled": True
    },
    {
        "name": "Public ATS Feeds (Workable / Greenhouse / Lever)",
        "type": "ats_feeds",
        "runner": query_public_ats_feeds,
        "enabled": True
    }
]
