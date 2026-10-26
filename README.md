# Grand Explorers' Society

*A natural-history archive for the curious.*

Founded on the spirit of scientific exploration, the Grand Explorers' Society (GES) is a web-based archive dedicated to discovering, documenting, classifying, and preserving knowledge of the world's flora and fauna, with particular attention given to rare, unusual, and previously undocumented species.

GES aims to make species information accessible to curious readers while maintaining a structured foundation for more detailed scientific exploration.

## About the Project

GES began as a learning project and gradually grew into a more substantial software and data-engineering undertaking. Along the way, I worked with: data processing, relational databases, API development, and frontend integration, using AI-assisted tools to accelerate implementation while continuing to learn and evaluate the technical decisions behind the system.

The project is an ongoing effort to build something useful, and make thoughtful decisions about data quality, provenance, performance, and responsible reuse.

## Features

- **Species catalogue** — Browse and search a structured archive of species.
- **Species profiles** — Explore scientific identity, descriptions, biological traits, classification, and vernacular names where information is available.
- **Multilingual groundwork** — Structured vernacular name data. The multilingual representation is yet to be developed.
- **Data pipeline** — Separate processing stages prepare, validate, normalize, and curate data before it reaches the production database.

## Scope and Limitations

The current focus is the species archive and its underlying data infrastructure. GES is not intended to replace authoritative taxonomic databases or serve as a definitive scientific reference.

Development is ongoing. Current limitations include:

- Explorer profiles and expedition records are planned but not yet implemented as complete features.
- Media, people, and source sections on species profiles remain future work where the necessary data and API support are not yet available.
- Species information varies in completeness depending on the underlying sources.
- Multilingual presentation and language-based vernacular-name selection require further development.
- AI-assisted discovery and other future research features are not yet part of the completed product.

Features may change as the project develops. Information should be checked against authoritative sources when used for research or other consequential purposes.

## Technical Overview

GES follows a data-processing and application architecture that separates source data from the final product.

**Data pipeline:** Raw source data is validated and normalized into Silver datasets, then curated into Gold datasets for the application's needs.

**Database:** SQLite provides relational storage for species, taxonomy, vernacular names, and trait observations.

**Backend:** FastAPI exposes the catalogue through REST API endpoints.

**Frontend:** A browser-based interface communicates with the backend to present the archive.


## Data Sources and Responsible Use

GES incorporates third-party biodiversity, taxonomic, and trait datasets. These sources are processed and curated for use within the archive, but such processing does not automatically change the original rights or licensing conditions.

Licensing and attribution requirements may differ between datasets and between content types, including taxonomic records, trait observations, text, photographs, and illustrations.

See [DATA_SOURCES.md](DATA_SOURCES.md) for the sources used, release information, applicable licences, attribution guidance, and processing notes. The project's software licence does not automatically apply to third-party data or other external content.

## Getting Started

### Requirements

- Python 3.11 or a compatible version supported by the pinned dependencies.
- Git.
- A modern web browser.
- The GES production SQLite database, provided separately.

### Run locally

**1. Clone the repository**

```cmd
git clone https://github.com/Mostly-carbon/Grand-explorers-society.git
cd Grand-explorers-society
```

**2. Set up the backend**

```cmd
cd backend
py -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**3. Provide the database**

Place the existing database at:

```text
backend/grand_explorers_society.db
```

The production database is not included in the repository. Obtain an authorized copy separately; the setup process does not require rebuilding the database.

**4. Start the API**

From the `backend` directory, run:

```cmd
venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API should be available at `http://127.0.0.1:8000`.

**5. Start the frontend**

Open a second Command Prompt in the repository's root directory and run:

```cmd
py frontend\dev_server.py
```

Open `http://127.0.0.1:5500` in your browser.

The local development configuration uses the frontend's local address for API access. Production deployment requires separate configuration.

## Current Status

GES is an early-stage, publicly accessible species archive. Its core catalogue and species-profile interface are operational, while further work remains on performance, data completeness, and additional features.

## Future Direction

Areas for further development include:

- Improving query performance, particularly for species search and retrieval.
- Expanding multilingual presentation and vernacular-name selection.
- Adding richer media displays and source attribution.
- Improving data quality, usability, security, and deployment reliability.
- Exploring research-oriented tools once the core archive is stable.
- Enriching the catalogue with additional validated data.

## Licence

The project's code is governed by the terms in [`LICENSE`](LICENSE). Third-party datasets and other external content may be subject to separate terms and are not automatically covered by the project's code licence.

## A Note from the Developer

GES started as a learning project and grew into something much bigger. Along the way, I've learned a lot about data processing, databases, APIs, and frontend development, with a little help from AI. Still learning and improving as I go! :)
The aim is to keep improving the archive carefully, document its limitations honestly, and make it a useful foundation for further exploration.

