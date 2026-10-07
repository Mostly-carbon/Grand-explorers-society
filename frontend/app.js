const API_BASE_URL = "http://127.0.0.1:8000";

const archiveSection = document.querySelector(".archive");
const detailSection = document.getElementById("species-detail");

const searchInput = document.getElementById("species-search");
const searchButton = document.getElementById("search-button");

const catalogueStatus = document.getElementById("catalogue-status");
const speciesList = document.getElementById("species-list");

const backButton = document.getElementById("back-button");
const detailContent = document.getElementById("detail-content");


// ------------------------------------------------------------
// Helpers
// ------------------------------------------------------------

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function displayValue(value) {
    if (value === null || value === undefined || value === "") {
        return "Not recorded";
    }

    return escapeHtml(value);
}


function hasData(object) {
    return Object.values(object).some(
        value =>
            value !== null &&
            value !== undefined &&
            value !== ""
    );
}


function detailField(label, value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "";
    }

    return `
        <div class="detail-field">
            <dt>${escapeHtml(label)}</dt>
            <dd>${displayValue(value)}</dd>
        </div>
    `;
}


// ------------------------------------------------------------
// Species catalogue
// ------------------------------------------------------------

async function loadSpecies(searchTerm = "") {
    catalogueStatus.textContent =
        "Consulting the Society's catalogue...";

    speciesList.innerHTML = "";

    try {
        const params = new URLSearchParams();

        params.set("limit", "50");

        if (searchTerm.trim() !== "") {
            params.set("q", searchTerm.trim());
        }

        const response = await fetch(
            `${API_BASE_URL}/species/?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(
                `Catalogue request failed with status ${response.status}`
            );
        }

        const data = await response.json();

        catalogueStatus.textContent =
            `${data.total.toLocaleString()} species recorded. ` +
            `Showing ${data.species.length.toLocaleString()}.`;

        renderSpeciesList(data.species);

    } catch (error) {
        console.error(
            "Failed to load species catalogue:",
            error
        );

        catalogueStatus.textContent =
            "The Society's catalogue could not be reached.";

        speciesList.innerHTML = `
            <div class="error-message">
                <h3>Catalogue unavailable</h3>
                <p>
                    The Society's records could not be retrieved.
                    Please make sure the API server is running.
                </p>
            </div>
        `;
    }
}


function renderSpeciesList(species) {
    if (!species || species.length === 0) {
        speciesList.innerHTML = `
            <div class="empty-message">
                <h3>No species found</h3>
                <p>
                    No catalogue entries matched your search.
                </p>
            </div>
        `;

        return;
    }

    speciesList.innerHTML = species.map((item, index) => {
        return `
            <article
                class="species-card"
                data-species-name="${escapeHtml(item.scientific_name)}"
            >
                <p class="species-number">
                    Record ${index + 1}
                </p>

                <h3>
                    ${displayValue(item.scientific_name)}
                </h3>

                ${
                    item.scientific_name_authorship
                        ? `
                            <p class="authorship">
                                ${displayValue(
                                    item.scientific_name_authorship
                                )}
                            </p>
                        `
                        : ""
                }

                <dl class="species-meta">

                    ${
                        item.rank
                            ? `
                                <div>
                                    <dt>Rank</dt>
                                    <dd>
                                        ${displayValue(item.rank)}
                                    </dd>
                                </div>
                            `
                            : ""
                    }

                    ${
                        item.kingdom
                            ? `
                                <div>
                                    <dt>Kingdom</dt>
                                    <dd>
                                        ${displayValue(item.kingdom)}
                                    </dd>
                                </div>
                            `
                            : ""
                    }

                    ${
                        item.taxonomic_status
                            ? `
                                <div>
                                    <dt>Taxonomic status</dt>
                                    <dd>
                                        ${displayValue(
                                            item.taxonomic_status
                                        )}
                                    </dd>
                                </div>
                            `
                            : ""
                    }

                </dl>

                <button
                    class="view-species-button"
                    type="button"
                >
                    Examine record
                </button>
            </article>
        `;
    }).join("");

    const cards = document.querySelectorAll(".species-card");

    cards.forEach(card => {
        card.addEventListener("click", () => {
            const scientificName =
                card.dataset.speciesName;

            loadSpeciesDetail(scientificName);
        });
    });
}


// ------------------------------------------------------------
// Species detail
// ------------------------------------------------------------

async function loadSpeciesDetail(scientificName) {
    archiveSection.classList.add("hidden");
    detailSection.classList.remove("hidden");

    detailContent.innerHTML = `
        <div class="loading-message">
            <p>
                Retrieving the Society's archive...
            </p>
        </div>
    `;

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    try {
        const encodedName =
            encodeURIComponent(scientificName);

        const response = await fetch(
            `${API_BASE_URL}/species/${encodedName}`
        );

        if (!response.ok) {
            throw new Error(
                `Species request failed with status ${response.status}`
            );
        }

        const species = await response.json();

        renderSpeciesDetail(species);

    } catch (error) {
        console.error(
            "Failed to load species detail:",
            error
        );

        detailContent.innerHTML = `
            <div class="error-message">
                <h3>Record unavailable</h3>

                <p>
                    The Society could not retrieve this species record.
                </p>

                <p>
                    <strong>
                        ${escapeHtml(scientificName)}
                    </strong>
                </p>
            </div>
        `;
    }
}


function renderSpeciesDetail(species) {
    const identity = species.identity;
    const about = species.about;
    const biology = species.biology;
    const classification = species.classification;
    const names = species.names || [];

    let html = "";


    // --------------------------------------------------------
    // Header
    // --------------------------------------------------------

    html += `
        <header class="species-detail-header">

            <p class="detail-record-id">
                Society record #${displayValue(species.id)}
            </p>

            <h1>
                ${displayValue(identity?.scientific_name)}
            </h1>

            ${
                identity?.scientific_name_authorship
                    ? `
                        <p class="detail-authorship">
                            ${displayValue(
                                identity.scientific_name_authorship
                            )}
                        </p>
                    `
                    : ""
            }

        </header>
    `;


    // --------------------------------------------------------
    // 1. Identity
    // --------------------------------------------------------

    if (identity) {
        html += `
            <section class="detail-section">

                <h2>Identity</h2>

                <div class="detail-grid">

                    ${detailField(
                        "Scientific name",
                        identity.scientific_name
                    )}

                    ${detailField(
                        "Authorship",
                        identity.scientific_name_authorship
                    )}

                    ${detailField(
                        "Taxonomic status",
                        identity.taxonomic_status
                    )}

                    ${detailField(
                        "Rank",
                        identity.rank
                    )}

                </div>

            </section>
        `;
    }


    // --------------------------------------------------------
    // 2. About
    // --------------------------------------------------------

    if (about && hasData(about)) {
        html += `
            <section class="detail-section">

                <h2>About</h2>

                <div class="detail-grid">

                    ${detailField(
                        "Description",
                        about.description
                    )}

                    ${detailField(
                        "Diet",
                        about.diet
                    )}

                    ${detailField(
                        "Lifespan",
                        about.lifespan
                    )}

                    ${detailField(
                        "Status",
                        about.status
                    )}

                </div>

            </section>
        `;
    }


    // --------------------------------------------------------
    // 3. Biology
    // --------------------------------------------------------

    if (
        biology &&
        biology.traits &&
        biology.traits.length > 0
    ) {
        html += `
            <section class="detail-section">

                <h2>Biology</h2>

                <div class="traits-list">
        `;

        biology.traits.forEach(trait => {

            html += `
                <article class="trait-card">

                    <div class="trait-heading">

                        <h3>
                            ${displayValue(trait.trait)}
                        </h3>

                        ${
                            trait.category
                                ? `
                                    <span class="trait-category">
                                        ${displayValue(
                                            trait.category
                                        )}
                                    </span>
                                `
                                : ""
                        }

                    </div>

                    <dl class="trait-details">

                        ${detailField(
                            "Numeric value",
                            trait.value_numeric
                        )}

                        ${detailField(
                            "Text value",
                            trait.value_text
                        )}

                        ${detailField(
                            "Unit",
                            trait.unit
                        )}

                        ${detailField(
                            "Context",
                            trait.context
                        )}

                        ${detailField(
                            "Sample size",
                            trait.sample_size
                        )}

                        ${detailField(
                            "Source",
                            trait.source
                        )}

                        ${detailField(
                            "Source record",
                            trait.source_record_id
                        )}

                        ${detailField(
                            "Notes",
                            trait.notes
                        )}

                    </dl>

                </article>
            `;
        });

        html += `
                </div>

            </section>
        `;
    }


    // --------------------------------------------------------
    // 4. Classification
    // --------------------------------------------------------

    if (
        classification &&
        hasData(classification)
    ) {
        html += `
            <section class="detail-section">

                <h2>Classification</h2>

                <div class="detail-grid">

                    ${detailField(
                        "Kingdom",
                        classification.kingdom
                    )}

                    ${detailField(
                        "Phylum",
                        classification.phylum
                    )}

                    ${detailField(
                        "Class",
                        classification.class_name
                    )}

                    ${detailField(
                        "Order",
                        classification.order
                    )}

                    ${detailField(
                        "Family",
                        classification.family
                    )}

                    ${detailField(
                        "Genus",
                        classification.genus
                    )}

                    ${detailField(
                        "Specific epithet",
                        classification.specific_epithet
                    )}

                    ${detailField(
                        "Infraspecific epithet",
                        classification.infraspecific_epithet
                    )}

                </div>

            </section>
        `;
    }


    // --------------------------------------------------------
    // 5. Names
    // --------------------------------------------------------

    if (names.length > 0) {
        html += `
            <section class="detail-section">

                <h2>Names</h2>

                <div class="names-table-wrapper">

                    <table class="names-table">

                        <thead>
                            <tr>
                                <th>Language</th>
                                <th>Name</th>
                                <th>Merged</th>
                            </tr>
                        </thead>

                        <tbody>
        `;

        names.forEach(name => {
            html += `
                <tr>

                    <td>
                        ${displayValue(name.language)}
                    </td>

                    <td>
                        ${displayValue(name.name)}
                    </td>

                    <td>
                        ${name.merged ? "Yes" : "No"}
                    </td>

                </tr>
            `;
        });

        html += `
                        </tbody>

                    </table>

                </div>

            </section>
        `;
    }


    // --------------------------------------------------------
    // Render
    // --------------------------------------------------------

    detailContent.innerHTML = html;
}


// ------------------------------------------------------------
// Search
// ------------------------------------------------------------

searchButton.addEventListener("click", () => {
    const searchTerm = searchInput.value.trim();

    detailSection.classList.add("hidden");
    archiveSection.classList.remove("hidden");

    loadSpecies(searchTerm);
});


searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        const searchTerm = searchInput.value.trim();

        detailSection.classList.add("hidden");
        archiveSection.classList.remove("hidden");

        loadSpecies(searchTerm);
    }
});


// ------------------------------------------------------------
// Back button
// ------------------------------------------------------------

backButton.addEventListener("click", () => {
    detailSection.classList.add("hidden");
    archiveSection.classList.remove("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});


// ------------------------------------------------------------
// Initial catalogue load
// ------------------------------------------------------------

loadSpecies();