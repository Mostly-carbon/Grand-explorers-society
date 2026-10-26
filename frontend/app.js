/* ============================================================
   GRAND EXPLORER'S SOCIETY
   Species Archive â€” Application Foundation
   ============================================================ */


/* CONFIGURATION */
const API_BASE_URL = (
    window.GES_API_BASE_URL ||
    (window.location.port === "5500"
        ? "http://127.0.0.1:8000"
        : "/api")
).replace(/\/+$/, "");

const PAGE_SIZE = 25;
const CACHE_PREFIX = "ges_species_";
const CATALOGUE_CACHE_KEY = "ges_catalogue_state";
const SEARCH_DEBOUNCE_MS = 250;


/* DOM REFERENCES */
const applicationLoading = document.getElementById("application-loading");
const application = document.getElementById("application");
const catalogueView = document.getElementById("catalogue-view");
const catalogueContent = document.getElementById("catalogue-content");
const catalogueStatus = document.getElementById("catalogue-status");
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("species-search");
const searchButton = document.getElementById("search-button");
const cataloguePagination = document.getElementById("catalogue-pagination");
const previousPageButton = document.getElementById("previous-page");
const nextPageButton = document.getElementById("next-page");
const paginationStatus = document.getElementById("pagination-status");
const speciesDetailView = document.getElementById("species-detail-view");
const speciesDetailLoading = document.getElementById("species-detail-loading");
const speciesDetailContent = document.getElementById("species-detail-content");
const speciesDetailError = document.getElementById("species-detail-error");
const detailRetryButton = document.getElementById("detail-retry-button");
const backButton = document.getElementById("back-button");
const connectionNotice = document.getElementById("connection-notice");
const homeLink = document.getElementById("home-link");
const siteTitleLink = document.getElementById("site-title-link");
const siteNavigation = document.querySelector(".site-navigation");
const siteMain = document.querySelector(".site-main");
const siteFooter = document.querySelector(".site-footer");

/* APPLICATION STATE */
const state = {
    query: "",
    page: 0,
    pageSize: PAGE_SIZE,
    total: 0,
    currentSpecies: null,
    currentSpeciesName: null,
    catalogueLoading: false,
    detailLoading: false,
    online: navigator.onLine,
    lastDetailRequest: null,
    catalogueRequestId: 0,
    detailRequestId: 0,
    searchTimer: null,
    currentSection: "species",
    hasMore: false,
};

/* STATIC INFORMATION PAGES */
const INFORMATION_PAGES = {
    sources: {
        title: "Sources and Acknowledgements",
        kicker: "Reference Register",
        introduction:
            "The Society's catalogue draws upon taxonomic and biological " +
            "reference data. These sources have different purposes and " +
            "levels of coverage; their records should be interpreted " +
            "according to the source and the evidence available.",
        sections: [
            {
                title: "Catalogue of Life",
                paragraphs: [
                    "Catalogue of Life provides the taxonomic backbone used " +
                    "by the Society's catalogue, including scientific names, " +
                    "taxonomic ranks, accepted-name relationships, and " +
                    "classification information where available.",
                    "Taxonomic names and relationships may change as " +
                    "scientific knowledge develops. The Society's records " +
                    "reflect the imported dataset and its processing at the " +
                    "time of publication; they should not be treated as a " +
                    "guarantee that every classification is current."
                ]
            },
            {
                title: "Biological trait references",
                paragraphs: [
                    "The archive incorporates biological trait observations " +
                    "from AnimalTraits and Elton-related bird and mammal " +
                    "datasets. These references contribute structured " +
                    "observations for selected organisms and biological " +
                    "characteristics.",
                    "Trait coverage is incomplete and varies by organism, " +
                    "characteristic, and source. An absent observation does " +
                    "not establish that a characteristic is absent in nature."
                ]
            },
            {
                title: "Attribution and provenance",
                paragraphs: [
                    "Where source information is available, the archive " +
                    "retains provenance alongside trait observations so that " +
                    "users can distinguish an observation from its originating " +
                    "reference or source record.",
                    "Source records may have their own authorship, licence, " +
                    "citation, and reuse requirements. Users intending to " +
                    "reuse source material should consult the originating " +
                    "provider's documentation and applicable terms."
                ]
            },
            {
                title: "Coverage and limitations",
                paragraphs: [
                    "The Society combines data that may differ in terminology, " +
                    "coverage, collection methods, and taxonomic treatment. " +
                    "Matching records across sources can introduce uncertainty, " +
                    "and not every source record can necessarily be resolved " +
                    "to an accepted species.",
                    "Only sources actually incorporated into the current " +
                    "archive should be regarded as active data sources. Future " +
                    "integrations, proposed references, and planned features " +
                    "are not represented as current sources."
                ]
            }
        ]
    },

    about: {
        title: "About the Society",
        kicker: "The Society and Its Charter",
        introduction:
            "The Grand Explorer's Society is a natural-history archive " +
            "devoted to the careful collection, organization, and study of " +
            "knowledge about the world's flora and fauna.",
        sections: [
            {
                title: "The Society's Charter",
                paragraphs: [
                    "To discover, document, classify, and preserve knowledge " +
                    "of the world's flora and fauna, with particular attention " +
                    "given to rare, unusual, and previously undocumented species."
                ]
            },
            {
                title: "A record of natural history",
                paragraphs: [
                    "The archive brings together scientific names, taxonomic " +
                    "classification, vernacular names, and selected biological " +
                    "observations in a catalogue designed for careful " +
                    "consultation.",
                    "Each species record is intended to serve as a point of " +
                    "reference: accessible to the curious reader while " +
                    "retaining the structure and provenance needed for more " +
                    "detailed investigation."
                ]
            },
            {
                title: "Method and evidence",
                paragraphs: [
                    "Natural-history knowledge is not static. Names are " +
                    "revised, classifications change, and observations may " +
                    "differ in quality or scope. The Society therefore treats " +
                    "its catalogue as a maintained body of reference material " +
                    "rather than a final or exhaustive account of life on Earth.",
                    "Where possible, information is kept connected to its " +
                    "source so that users can understand the evidence behind " +
                    "an observation and investigate the original reference."
                ]
            },
            {
                title: "The archive today",
                paragraphs: [
                    "The Grand Explorer's Society is presented as a historical-" +
                    "themed digital archive. Its Society narrative and period " +
                    "aesthetic are part of the project's presentation; they " +
                    "should not be understood as evidence of a historical " +
                    "institution or of field expeditions that have not been " +
                    "documented by the project.",
                    "The present catalogue concentrates on species records. " +
                    "Additional areas of the archive may be introduced only " +
                    "when their data and functionality are available."
                ]
            }
        ]
    },

    legal: {
        title: "Terms and Conditions",
        kicker: "Conditions of Use",
        introduction:
            "These terms govern access to and use of the Grand Explorer's " +
            "Society Natural History Archive. By using the website, you " +
            "agree to comply with these terms and applicable law.",
        sections: [
            {
                title: "1. Purpose of the archive",
                paragraphs: [
                    "The archive is provided for educational, informational, " +
                    "and research-reference purposes. It is not a substitute " +
                    "for authoritative taxonomic databases, professional " +
                    "scientific advice, or consultation of original research."
                ]
            },
            {
                title: "2. Acceptable use",
                paragraphs: [
                    "You must use the website lawfully and must not attempt " +
                    "to disrupt its operation, bypass access controls, " +
                    "interfere with other users, introduce malicious code, " +
                    "or access systems or data without authorization.",
                    "You must not misrepresent archive records, source " +
                    "material, or the Society's identity in a way that " +
                    "misleads others about the origin or reliability of " +
                    "information."
                ]
            },
            {
                title: "3. Intellectual property",
                paragraphs: [
                    "The website's original presentation, layout, original " +
                    "text, and software may be protected by applicable " +
                    "intellectual-property laws. Unless expressly permitted " +
                    "by law or by the relevant rights holder, you may not " +
                    "reproduce or redistribute protected material beyond " +
                    "the scope of the applicable permission.",
                    "Scientific names, factual information, and third-party " +
                    "dataset material may be subject to different legal " +
                    "rules and licence terms. Nothing in these terms grants " +
                    "ownership of third-party material or overrides a " +
                    "source provider's licence.",
                    "You are responsible for checking attribution, licence, " +
                    "and reuse requirements before copying, publishing, " +
                    "redistributing, or commercially using data from the archive."
                ]
            },
            {
                title: "4. Sources and attribution",
                paragraphs: [
                    "Where source details are supplied, they are provided " +
                    "to help users identify the origin of information. " +
                    "Attribution details may be incomplete or may change " +
                    "as the archive is maintained.",
                    "You should consult the original source and its current " +
                    "terms before relying on or reusing third-party data. " +
                    "A source being listed in the archive does not imply " +
                    "that its provider endorses the Society."
                ]
            },
            {
                title: "5. Accuracy and availability",
                paragraphs: [
                    "The archive is provided on an 'as is' and 'as available' " +
                    "basis, to the extent permitted by applicable law. " +
                    "Reasonable care may be taken in preparing and maintaining " +
                    "records, but errors, omissions, outdated classifications, " +
                    "incomplete coverage, and mismatches between sources may occur.",
                    "The website or its data may be changed, suspended, or " +
                    "made unavailable without notice. No guarantee is made " +
                    "that the service will be uninterrupted, error-free, " +
                    "complete, or suitable for a particular purpose."
                ]
            },
            {
                title: "6. No professional advice",
                paragraphs: [
                    "Information in the archive is not a substitute for " +
                    "professional advice or verification against primary " +
                    "literature and authoritative references. Users are " +
                    "responsible for independently checking information " +
                    "before using it in scientific, educational, commercial, " +
                    "conservation, or other consequential decisions."
                ]
            },
            {
                title: "7. Limitation of liability",
                paragraphs: [
                    "To the fullest extent permitted by applicable law, " +
                    "the website operator shall not be liable for indirect, " +
                    "incidental, special, consequential, or punitive loss, " +
                    "or for loss of data, profits, or opportunities arising " +
                    "from use of, or inability to use, the archive.",
                    "Nothing in these terms excludes or limits liability " +
                    "that cannot lawfully be excluded or limited, including " +
                    "any rights or remedies that cannot be waived under " +
                    "applicable consumer-protection or other mandatory law."
                ]
            },
            {
                title: "8. External sources and websites",
                paragraphs: [
                    "The archive may identify or refer to external datasets, " +
                    "publications, or websites. Those resources are controlled " +
                    "by their respective providers. The Society does not " +
                    "control their availability, content, or policies and " +
                    "does not automatically endorse their statements."
                ]
            },
            {
                title: "9. Changes to these terms",
                paragraphs: [
                    "These terms may be updated as the website develops. " +
                    "The version published on this page applies from the " +
                    "time it is made available. Where appropriate, material " +
                    "changes should be accompanied by an updated effective date."
                ]
            },
            {
                title: "10. Applicable law",
                paragraphs: [
                    "These terms are subject to applicable law. Any mandatory " +
                    "rights or legal requirements that apply to your use of " +
                    "the website remain unaffected by these terms.",
                    "Before public deployment, the website operator should " +
                    "identify the appropriate governing law, dispute process, " +
                    "operator details, privacy requirements, and any other " +
                    "disclosures required for the intended audience and " +
                    "jurisdiction."
                ]
            },
            {
                title: "Privacy and personal information",
                paragraphs: [
                    "The archive should not request personal information " +
                    "unless it is necessary for a clearly stated purpose. " +
                    "If the deployed service collects personal information, " +
                    "uses analytics, sets non-essential cookies, or provides " +
                    "user accounts or contact forms, a separate privacy " +
                    "notice should explain those practices and any applicable " +
                    "rights.",
                    "This page is not a substitute for a privacy notice " +
                    "tailored to the website's actual data collection, " +
                    "hosting, and analytics configuration."
                ]
            }
        ]
    }
};

/* STARTUP */
document.addEventListener("DOMContentLoaded", initializeApplication);

async function initializeApplication() {
    bindApplicationEvents();
    initializePrimaryNavigation();
    updateConnectionState();
    showApplication();

    const route = resolveCurrentRoute();

    state.query = route.query || "";
    state.page = route.page || 0;
    syncSearchInput();

    if (route.section !== "species") {
        showSection(route.section, { updateHistory: false });
        return;
    }

    if (route.speciesName) {
        await loadSpeciesDetail(route.speciesName);
        return;
    }

    showSection("species", { updateHistory: false });
    renderCatalogueSkeletons();
    await loadCatalogue();
}

function showApplication() {
    applicationLoading?.classList.add("hidden");
    application?.classList.remove("hidden");
}

/* EVENTS */
function bindApplicationEvents() {
    searchForm?.addEventListener("submit", handleSearchSubmit);
    previousPageButton?.addEventListener("click", handlePreviousPage);
    nextPageButton?.addEventListener("click", handleNextPage);
    backButton?.addEventListener("click", handleBackToCatalogue);
    detailRetryButton?.addEventListener("click", handleDetailRetry);
    homeLink?.addEventListener("click", handleHomeNavigation);
    siteTitleLink?.addEventListener("click", handleHomeNavigation);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    window.addEventListener("popstate", handleBrowserNavigation);
}

function syncSearchInput() {
    if (searchInput) {
        searchInput.value = state.query;
    }
}

/* PRIMARY NAVIGATION */
function initializePrimaryNavigation() {
    if (!siteNavigation) {
        return;
    }

    const allowedSections = new Set([
        "species",
        "sources",
        "about",
        "legal"
    ]);

    siteNavigation.querySelectorAll("[data-section]").forEach(link => {
        const section = cleanText(link.dataset.section).toLowerCase();

        if (!allowedSections.has(section)) {
            link.remove();
            return;
        }

        link.href = getSectionPath(section);

        link.addEventListener("click", event => {
            event.preventDefault();
            showSection(section);
        });
    });

    updateNavigationState(state.currentSection);
}

function getSectionPath(section) {
    const paths = {
        species: "/",
        sources: "/sources",
        about: "/about",
        legal: "/legal"
    };

    return paths[section] || "/";
}

/* ROUTE RESOLUTION */
function resolveCurrentRoute() {
    const pathname = window.location.pathname;
    const normalizedPath = pathname.replace(/\/+$/, "") || "/";
    const speciesName = extractSpeciesNameFromPath(normalizedPath);

    const parameters = new URLSearchParams(window.location.search);
    const requestedPage = Number.parseInt(parameters.get("page"), 10);

    const query = parameters.get("q") || "";
    const page = Number.isInteger(requestedPage) && requestedPage > 0
        ? requestedPage - 1
        : 0;

    if (speciesName) {
        return {
            section: "species",
            speciesName,
            query: "",
            page: 0
        };
    }

    const routeMap = {
        "/": "species",
        "/sources": "sources",
        "/about": "about",
        "/legal": "legal"
    };

    return {
        section: routeMap[normalizedPath.toLowerCase()] || "species",
        speciesName: null,
        query,
        page
    };
}

function showSection(section, options = {}) {
    const allowedSections = new Set([
        "species",
        "sources",
        "about",
        "legal"
    ]);

    if (!allowedSections.has(section)) {
        section = "species";
    }

    const updateHistory = options.updateHistory !== false;
    const previousSection = state.currentSection;

    state.currentSection = section;

    if (section !== "species") {
        invalidateDetailRequest();
        state.currentSpecies = null;
        state.currentSpeciesName = null;
        hideSpeciesDetail();
    }

    if (updateHistory) {
        const targetPath = section === "species"
            ? buildCatalogueUrl(state.query, state.page)
            : getSectionPath(section);

        const currentPath =
            window.location.pathname + window.location.search;

        if (currentPath !== targetPath) {
            window.history.pushState(
                {
                    section,
                    query: state.query,
                    page: state.page
                },
                "",
                targetPath
            );
        }
    }

    updateNavigationState(section);
    clearInformationPage();

    if (section === "species") {
        syncSearchInput();
        showCataloguePage();
    } else {
        showInformationPage(section);
    }

    if (previousSection !== section) {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
}

function updateNavigationState(section) {
    if (!siteNavigation) {
        return;
    }

    siteNavigation.querySelectorAll("[data-section]").forEach(link => {
        const isCurrent = link.dataset.section === section;

        link.classList.toggle("navigation-link-current", isCurrent);

        if (isCurrent) {
            link.setAttribute("aria-current", "page");
        } else {
            link.removeAttribute("aria-current");
        }
    });
}

function showCataloguePage() {
    clearInformationPage();

    catalogueView?.classList.remove("hidden");
    speciesDetailView?.classList.add("hidden");
}

function showInformationPage(section) {
    catalogueView?.classList.add("hidden");
    speciesDetailView?.classList.add("hidden");

    const page = INFORMATION_PAGES[section];

    if (!page || !siteMain) {
        return;
    }

    const pageElement = document.createElement("section");
    pageElement.id = "information-page";
    pageElement.className = "information-page";
    pageElement.setAttribute("aria-labelledby", "information-page-title");

    const header = document.createElement("header");
    header.className = "catalogue-header information-page-header";

    const headingGroup = document.createElement("div");
    headingGroup.className = "catalogue-heading-group";

    const kicker = document.createElement("div");
    kicker.className = "catalogue-kicker";
    kicker.textContent = page.kicker;

    const title = document.createElement("h1");
    title.id = "information-page-title";
    title.className = "catalogue-title";
    title.textContent = page.title;

    const introduction = document.createElement("p");
    introduction.className = "catalogue-description";
    introduction.textContent = page.introduction;

    headingGroup.append(kicker, title, introduction);
    header.appendChild(headingGroup);
    pageElement.appendChild(header);

    const content = document.createElement("div");
    content.className = "information-page-content";

    page.sections.forEach(sectionData => {
        const sectionElement = document.createElement("section");
        sectionElement.className = "information-page-section";

        const sectionHeading = document.createElement("h2");
        sectionHeading.className = "detail-section-title";
        sectionHeading.textContent = sectionData.title;

        sectionElement.appendChild(sectionHeading);

        sectionData.paragraphs.forEach(paragraphText => {
            const paragraph = document.createElement("p");
            paragraph.textContent = paragraphText;
            sectionElement.appendChild(paragraph);
        });

        content.appendChild(sectionElement);
    });

    if (section === "legal") {
        const effectiveDate = document.createElement("p");
        effectiveDate.className = "information-page-effective-date";
        effectiveDate.textContent = "Last updated: 11 October 2026";

        content.appendChild(effectiveDate);
    }

    pageElement.appendChild(content);
    siteMain.appendChild(pageElement);
}

function clearInformationPage() {
    document.getElementById("information-page")?.remove();
}

function handleHomeNavigation(event) {
    event.preventDefault();
    showSection("species");
}

function handleBackToCatalogue() {
    showSection("species");
}

/* BROWSER BACK / FORWARD */
function handleBrowserNavigation(event) {
    const route = resolveCurrentRoute();

    /*
     * When navigating back or forward to a species record, restore the
     * catalogue query/page associated with that history entry where present.
     * Directly opened species URLs default to the first unfiltered page.
     */
    if (route.speciesName) {
        const historyState = event.state;

        if (historyState && historyState.section === "species") {
            state.query = cleanText(historyState.query);
            state.page = normalizeNonNegativeInteger(historyState.page);
        } else {
            state.query = "";
            state.page = 0;
        }

        syncSearchInput();
        clearInformationPage();
        state.currentSection = "species";
        updateNavigationState("species");
        showCataloguePage();
        loadSpeciesDetail(route.speciesName);
        return;
    }

    state.query = route.query || "";
    state.page = route.page || 0;
    syncSearchInput();

    if (route.section !== "species") {
        showSection(route.section, { updateHistory: false });
        return;
    }

    clearInformationPage();
    state.currentSection = "species";
    updateNavigationState("species");
    showCataloguePage();

    invalidateDetailRequest();
    state.currentSpecies = null;
    state.currentSpeciesName = null;
    hideSpeciesDetail();

    renderCatalogueSkeletons();
    loadCatalogue();
}

function navigateToCatalogue() {
    showSection("species");
}

function getCataloguePath() {
    return buildCatalogueUrl(state.query, state.page);
}

function invalidateDetailRequest() {
    state.detailRequestId += 1;
    state.lastDetailRequest = null;
    state.detailLoading = false;

    hideSpeciesDetailLoading();
}

/* URL HELPERS */
function buildCatalogueUrl(query = state.query, page = state.page) {
    const parameters = new URLSearchParams();
    const normalizedQuery = cleanText(query);
    const normalizedPage = normalizeNonNegativeInteger(page);

    if (normalizedQuery) {
        parameters.set("q", normalizedQuery);
    }

    if (normalizedPage > 0) {
        parameters.set("page", String(normalizedPage + 1));
    }

    const search = parameters.toString();

    return search ? `/?${search}` : "/";
}

function buildSpeciesUrl(scientificName) {
    return "/species/" + encodeURIComponent(String(scientificName));
}

function extractSpeciesNameFromPath(pathname) {
    if (typeof pathname !== "string") {
        return null;
    }

    const normalizedPath = pathname.replace(/\/+$/, "");
    const match = normalizedPath.match(/^\/species\/(.+)$/i);

    if (!match) {
        return null;
    }

    const encodedName = match[1];

    if (!encodedName || encodedName.includes("/")) {
        return null;
    }

    try {
        const decoded = decodeURIComponent(encodedName).trim();

        return decoded && !decoded.includes("/")
            ? decoded
            : null;
    } catch {
        return null;
    }
}

/* CATALOGUE HISTORY */
function updateCatalogueHistory() {
    const targetPath = buildCatalogueUrl(state.query, state.page);
    const currentPath =
        window.location.pathname + window.location.search;

    if (currentPath === targetPath) {
        return;
    }

    window.history.pushState(
        {
            section: "species",
            query: state.query,
            page: state.page
        },
        "",
        targetPath
    );
}

/* SEARCH */
function handleSearchSubmit(event) {
    event.preventDefault();

    if (!searchInput) {
        return;
    }

    clearTimeout(state.searchTimer);

    const query = searchInput.value.trim();

    state.searchTimer = setTimeout(
        () => performSearch(query),
        SEARCH_DEBOUNCE_MS
    );
}

async function performSearch(query) {
    clearTimeout(state.searchTimer);
    state.searchTimer = null;

    state.query = cleanText(query);
    state.page = 0;
    state.hasMore = false;

    state.catalogueRequestId += 1;
    state.catalogueLoading = false;
    setCatalogueLoadingState(false);

    invalidateDetailRequest();
    state.currentSpecies = null;
    state.currentSpeciesName = null;

    showSection("species");
    updateCatalogueHistory();
    syncSearchInput();
    renderCatalogueSkeletons();
    updatePagination();

    await loadCatalogue();
}

/* CATALOGUE API */
async function loadCatalogue(append = false) {
    const requestId = ++state.catalogueRequestId;
    const requestedQuery = state.query;
    const requestedPage = state.page;
    const requestedPageSize = state.pageSize;
    const offset = requestedPage * requestedPageSize;

    state.catalogueLoading = true;
    setCatalogueLoadingState(true);
    updatePagination();

    try {
        const parameters = new URLSearchParams({
            limit: String(requestedPageSize),
            offset: String(offset),
            sort: "scientific_name",
            order: "asc"
        });

        if (requestedQuery) {
            parameters.set("q", requestedQuery);
        }

        const response = await fetch(
            `${API_BASE_URL}/species/?${parameters.toString()}`,
            {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                `Catalogue request failed with status ${response.status}`
            );
        }

        const data = await response.json();

        if (requestId !== state.catalogueRequestId) {
            return;
        }

        if (!isValidCatalogueResponse(data)) {
            throw new Error(
                "The catalogue API returned an invalid response."
            );
        }

        state.total = normalizeNonNegativeInteger(data.total);
        state.hasMore = data.has_more === true;

        renderCatalogue(data, false, append);

        saveCatalogueCache(
            data,
            requestedQuery,
            requestedPage,
            requestedPageSize
        );
    } catch (error) {
        if (requestId !== state.catalogueRequestId) {
            return;
        }

        console.error("Unable to load catalogue:", error);

        if (append) {
            state.page = Math.max(0, requestedPage - 1);
            updateCatalogueHistory();
        }

        handleCatalogueFailure(
            requestedQuery,
            requestedPage
        );

    } finally {
        if (requestId === state.catalogueRequestId) {
            state.catalogueLoading = false;
            setCatalogueLoadingState(false);
            updatePagination();
            updateShowMoreButton();
        }
    }
}


function isValidCatalogueResponse(data) {
    return Boolean(
        data &&
        typeof data === "object" &&
        Array.isArray(data.species) &&
        data.species.every(
            record => record && typeof record === "object"
        )
    );
}

/* CATALOGUE LOADING STATE */
function setCatalogueLoadingState(isLoading) {
    catalogueContent?.classList.toggle(
        "catalogue-refreshing",
        isLoading
    );

    if (searchButton) {
        searchButton.disabled = false;
    }

    if (cataloguePagination) {
        cataloguePagination.setAttribute(
            "aria-busy",
            isLoading ? "true" : "false"
        );
    }
}

/* CATALOGUE FAILURE */
function handleCatalogueFailure(
    requestedQuery = state.query,
    requestedPage = state.page
) {
    const cached = loadCatalogueCache();

    if (
        cached &&
        Array.isArray(cached.species) &&
        cached.query === requestedQuery &&
        Number(cached.page) === requestedPage
    ) {
        state.total = normalizeNonNegativeInteger(cached.total);
        renderCatalogue(cached, true);
        return;
    }

    renderCatalogueError();
}

/* CATALOGUE CACHE */
function saveCatalogueCache(
    data,
    query = state.query,
    page = state.page,
    pageSize = state.pageSize
) {
    if (!isValidCatalogueResponse(data)) {
        return;
    }

    try {
        const cacheData = {
            query,
            page,
            pageSize,
            total: normalizeNonNegativeInteger(data.total),
            limit: data.limit,
            offset: data.offset,
            species: data.species,
            savedAt: Date.now()
        };

        localStorage.setItem(
            CATALOGUE_CACHE_KEY,
            JSON.stringify(cacheData)
        );
    } catch (error) {
        console.warn("Catalogue cache could not be saved:", error);
    }
}

function loadCatalogueCache() {
    try {
        const raw = localStorage.getItem(CATALOGUE_CACHE_KEY);

        if (!raw) {
            return null;
        }

        const parsed = JSON.parse(raw);

        if (
            !parsed ||
            !Array.isArray(parsed.species) ||
            typeof parsed.query !== "string" ||
            !Number.isInteger(Number(parsed.page)) ||
            !parsed.species.every(
                record => record && typeof record === "object"
            )
        ) {
            return null;
        }

        return parsed;
    } catch (error) {
        console.warn("Catalogue cache could not be read:", error);
        return null;
    }
}

/* SPECIES RECORD CACHE */
function speciesCacheKey(scientificName) {
    return CACHE_PREFIX + encodeURIComponent(String(scientificName));
}

function saveSpeciesCache(species) {
    const scientificName = species?.identity?.scientific_name;

    if (
        typeof scientificName !== "string" ||
        !scientificName.trim()
    ) {
        return;
    }

    try {
        localStorage.setItem(
            speciesCacheKey(scientificName),
            JSON.stringify({
                species,
                savedAt: Date.now()
            })
        );
    } catch (error) {
        console.warn("Species cache could not be saved:", error);
    }
}

function loadSpeciesCache(scientificName) {
    try {
        const raw = localStorage.getItem(
            speciesCacheKey(scientificName)
        );

        if (!raw) {
            return null;
        }

        const parsed = JSON.parse(raw);
        const species = parsed?.species;

        if (
            !species ||
            typeof species !== "object" ||
            typeof species.identity?.scientific_name !== "string"
        ) {
            return null;
        }

        if (species.identity.scientific_name !== scientificName) {
            return null;
        }

        return species;
    } catch (error) {
        console.warn("Species cache could not be read:", error);
        return null;
    }
}

/* NETWORK STATE */
function handleOnline() {
    state.online = true;
    updateConnectionState();
    connectionNotice?.classList.add("hidden");
}

function handleOffline() {
    state.online = false;
    updateConnectionState();

    if (connectionNotice) {
        connectionNotice.textContent = "You are currently offline.";
        connectionNotice.classList.remove("hidden");
    }
}

function updateConnectionState() {
    state.online = navigator.onLine;

    application?.classList.toggle(
        "application-offline",
        !state.online
    );
}

/* CATALOGUE RENDERING */

function renderCatalogue(data, fromCache = false, append = false) {
    if (!catalogueContent) {
        return;
    }

    const species = Array.isArray(data?.species)
        ? data.species
        : [];

    const total = normalizeNonNegativeInteger(data?.total);

    updateCatalogueStatus(total, fromCache);

    if (!append) {
        catalogueContent.replaceChildren();
    }

    if (species.length === 0 && !append) {
        renderCatalogueEmpty();
        updatePagination();
        updateShowMoreButton();
        return;
    }

    const fragment = document.createDocumentFragment();

    species.forEach(record => {
        fragment.appendChild(createSpeciesRow(record));
    });

    catalogueContent.appendChild(fragment);

    updatePagination();
    updateShowMoreButton();
}


function updateShowMoreButton() {
    let button = document.getElementById("catalogue-show-more");

    if (!button) {
        button = document.createElement("button");
        button.id = "catalogue-show-more";
        button.type = "button";
        button.className = "text-button";
        button.textContent = "Show more";

        button.addEventListener("click", async () => {
            if (state.catalogueLoading || !state.hasMore) {
                return;
            }

            state.page += 1;
            updateCatalogueHistory();
            await loadCatalogue(true);
        });


    }
    if (catalogueContent && button.previousElementSibling !== catalogueContent) {
        catalogueContent.after(button);
    }

    button.hidden = !state.hasMore;
    button.disabled = state.catalogueLoading;
}



/* CATALOGUE STATUS */
function updateCatalogueStatus(total, fromCache = false) {
    if (!catalogueStatus) {
        return;
    }

    const count = normalizeNonNegativeInteger(total);
    let statusText;

    if (state.query) {
        if (count > 500) {
            statusText = "500+ matching records";
        } else if (count === 1) {
            statusText = "1 record found";
        } else {
            statusText = `${formatNumber(count)} records found`;
        }
    } else {
        statusText = count === 1
            ? "1 species recorded"
            : `${formatNumber(count)} species recorded`;
    }

    if (fromCache) {
        statusText += " Â· cached";
    }

    catalogueStatus.textContent = statusText;
}


/* SPECIES ROW */
function createSpeciesRow(speciesRecord) {
    const row = document.createElement("article");
    row.className = "species-row";

    const identity = document.createElement("div");
    identity.className = "species-row-identity";

    const scientificName = document.createElement("h2");
    scientificName.className = "species-row-name";

    const scientificNameText = cleanText(
        speciesRecord.scientific_name
    );

    scientificName.textContent = scientificNameText || "Unnamed record";
    scientificName.setAttribute("title", scientificNameText);

    const authorshipText = cleanText(
        speciesRecord.scientific_name_authorship
    );

    if (authorshipText) {
        const authorship = document.createElement("span");
        authorship.className = "species-row-authorship";
        authorship.textContent = authorshipText;
        identity.append(scientificName, authorship);
    } else {
        identity.appendChild(scientificName);
    }

    const classification = document.createElement("div");
    classification.className = "species-row-classification";

    classification.appendChild(
        createMetadataItem("Rank", speciesRecord.rank)
    );

    classification.appendChild(
        createMetadataItem("Kingdom", speciesRecord.kingdom)
    );

    classification.appendChild(
        createMetadataItem(
            "Taxonomic status",
            speciesRecord.taxonomic_status
        )
    );

    const recordStatus = document.createElement("div");
    recordStatus.className = "species-row-status";

    const statusText = cleanText(speciesRecord.status);

    if (statusText) {
        const statusLabel = document.createElement("span");
        statusLabel.className = "species-status-label";
        statusLabel.textContent = statusText;
        recordStatus.appendChild(statusLabel);
    }

    const actionArea = document.createElement("div");
    actionArea.className = "species-row-action";

    const examineButton = document.createElement("button");
    examineButton.type = "button";
    examineButton.className = "text-button species-examine-button";
    examineButton.textContent = "Examine";

    examineButton.setAttribute(
        "aria-label",
        `Examine ${scientificNameText || "species record"}`
    );

    examineButton.disabled = !scientificNameText;

    examineButton.addEventListener("click", () => {
        openSpeciesRecord(scientificNameText);
    });

    actionArea.appendChild(examineButton);

    row.append(
        identity,
        classification,
        recordStatus,
        actionArea
    );

    return row;
}

/* METADATA ITEM */
function createMetadataItem(label, value) {
    const item = document.createElement("div");
    item.className = "species-metadata-item";

    const labelElement = document.createElement("span");
    labelElement.className = "species-metadata-label";
    labelElement.textContent = label;

    const valueElement = document.createElement("span");
    valueElement.className = "species-metadata-value";
    valueElement.textContent = formatMetadataValue(value);

    item.append(labelElement, valueElement);

    return item;
}

/* EMPTY STATE */
function renderCatalogueEmpty() {
    if (!catalogueContent) {
        return;
    }

    catalogueContent.replaceChildren();

    const emptyState = document.createElement("section");
    emptyState.className = "empty-state";

    const heading = document.createElement("h2");
    heading.textContent = "No records found";

    const message = document.createElement("p");

    message.textContent = state.query
        ? `No species matched "${state.query}". Try a scientific name or common name.`
        : "The catalogue contains no records to display.";

    emptyState.append(heading, message);

    if (state.query) {
        const clearButton = document.createElement("button");
        clearButton.type = "button";
        clearButton.className = "text-button";
        clearButton.textContent = "Clear search";

        clearButton.addEventListener("click", () => {
            if (searchInput) {
                searchInput.value = "";
            }

            performSearch("");
        });

        emptyState.appendChild(clearButton);
    }

    catalogueContent.appendChild(emptyState);
}

/* CATALOGUE ERROR */
function renderCatalogueError() {
    if (!catalogueContent) {
        return;
    }

    catalogueContent.replaceChildren();

    const errorState = document.createElement("section");
    errorState.className = "error-state";

    const heading = document.createElement("h2");
    heading.textContent = "Catalogue unavailable";

    const message = document.createElement("p");
    message.textContent =
        "The Society catalogue could not be reached. " +
        "Please check that the archive service is running.";

    const retryButton = document.createElement("button");
    retryButton.type = "button";
    retryButton.className = "text-button";
    retryButton.textContent = "Try again";

    retryButton.addEventListener("click", () => {
        renderCatalogueSkeletons();
        loadCatalogue();
    });

    errorState.append(heading, message, retryButton);
    catalogueContent.appendChild(errorState);

    if (catalogueStatus) {
        catalogueStatus.textContent = "Unable to retrieve catalogue";
    }

    updatePagination();
}

/* CATALOGUE SKELETONS */
function renderCatalogueSkeletons() {
    if (!catalogueContent) {
        return;
    }

    catalogueContent.replaceChildren();

    const fragment = document.createDocumentFragment();

    for (let index = 0; index < 8; index += 1) {
        fragment.appendChild(createCatalogueSkeleton());
    }

    catalogueContent.appendChild(fragment);
}

function createCatalogueSkeleton() {
    const skeleton = document.createElement("article");
    skeleton.className = "species-row species-row-skeleton";
    skeleton.setAttribute("aria-hidden", "true");

    const identity = document.createElement("div");
    identity.className = "species-row-identity";

    identity.append(
        createSkeletonBlock("skeleton-name"),
        createSkeletonBlock("skeleton-authorship")
    );

    const classification = document.createElement("div");
    classification.className = "species-row-classification";

    for (let index = 0; index < 3; index += 1) {
        classification.appendChild(
            createSkeletonBlock("skeleton-metadata skeleton-meta")
        );
    }

    const status = document.createElement("div");
    status.className = "species-row-status";
    status.appendChild(createSkeletonBlock("skeleton-status"));

    const action = document.createElement("div");
    action.className = "species-row-action";
    action.appendChild(createSkeletonBlock("skeleton-action"));

    skeleton.append(identity, classification, status, action);

    return skeleton;
}

function createSkeletonBlock(className) {
    const block = document.createElement("span");
    block.className = `skeleton-block ${className}`;
    return block;
}

/* PAGINATION */

function updatePagination() {
    if (previousPageButton) {
        previousPageButton.hidden = true;
        previousPageButton.disabled = true;
    }

    if (nextPageButton) {
        nextPageButton.hidden = true;
        nextPageButton.disabled = true;
    }

    if (paginationStatus) {
        const loadedCount = catalogueContent
            ? catalogueContent.querySelectorAll(".species-row:not(.species-row-skeleton)").length
            : 0;

        paginationStatus.textContent = loadedCount > 0
            ? `${formatNumber(loadedCount)} records displayed`
            : "No records displayed";
    }

    updateShowMoreButton();
}


async function handlePreviousPage() {
    if (state.page <= 0 || state.catalogueLoading) {
        return;
    }

    state.page -= 1;
    updateCatalogueHistory();
    renderCatalogueSkeletons();

    await loadCatalogue();
    scrollToCatalogue();
}

async function handleNextPage() {
    const totalPages = Math.ceil(state.total / state.pageSize);

    if (
        state.page + 1 >= totalPages ||
        state.catalogueLoading
    ) {
        return;
    }

    state.page += 1;
    updateCatalogueHistory();
    renderCatalogueSkeletons();

    await loadCatalogue();
    scrollToCatalogue();
}

/* CATALOGUE SCROLL */
function scrollToCatalogue() {
    if (!catalogueView) {
        return;
    }

    const top =
        catalogueView.getBoundingClientRect().top +
        window.scrollY -
        24;

    window.scrollTo({
        top: Math.max(top, 0),
        behavior: "smooth"
    });
}

/* SPECIES RECORD NAVIGATION */
function openSpeciesRecord(scientificName) {
    const name = cleanText(scientificName);

    if (!name) {
        return;
    }

    state.currentSection = "species";
    updateNavigationState("species");
    clearInformationPage();

    window.history.pushState(
        {
            section: "species",
            species: name,
            query: state.query,
            page: state.page
        },
        "",
        buildSpeciesUrl(name)
    );

    loadSpeciesDetail(name);

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

/* DETAIL VIEW STATE */
function showSpeciesDetail() {
    catalogueView?.classList.add("hidden");
    speciesDetailView?.classList.remove("hidden");
}

function hideSpeciesDetail() {
    speciesDetailView?.classList.add("hidden");

    if (state.currentSection === "species") {
        catalogueView?.classList.remove("hidden");
    }

    speciesDetailLoading?.classList.add("hidden");
    speciesDetailError?.classList.add("hidden");
}

/* DETAIL LOADING */
async function loadSpeciesDetail(scientificName) {
    const name = cleanText(scientificName);

    if (!name) {
        return;
    }

    const requestId = ++state.detailRequestId;

    state.currentSection = "species";
    state.currentSpeciesName = name;
    state.currentSpecies = null;
    state.detailLoading = true;
    state.lastDetailRequest = name;

    updateNavigationState("species");
    clearInformationPage();
    showSpeciesDetail();
    showSpeciesDetailLoading();

    speciesDetailContent?.replaceChildren();

    const cached = loadSpeciesCache(name);

    if (cached) {
        state.currentSpecies = cached;
        renderSpeciesDetail(cached, true);
        hideSpeciesDetailLoading();
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/species/${encodeURIComponent(name)}`,
            {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            }
        );

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error("SPECIES_NOT_FOUND");
            }

            throw new Error(
                `Species request failed with status ${response.status}`
            );
        }

        const species = await response.json();

        if (requestId !== state.detailRequestId) {
            return;
        }

        if (
            !species ||
            typeof species !== "object" ||
            !species.identity ||
            typeof species.identity.scientific_name !== "string" ||
            !species.identity.scientific_name.trim() ||
            species.identity.scientific_name.trim() !== name
        ) {
            throw new Error("Invalid species record");
        }

        state.currentSpecies = species;

        saveSpeciesCache(species);
        renderSpeciesDetail(species, false);
    } catch (error) {
        if (requestId !== state.detailRequestId) {
            return;
        }

        console.error("Unable to load species:", error);

        if (cached) {
            state.currentSpecies = cached;
            renderSpeciesDetail(cached, true);
        } else {
            renderSpeciesDetailError(error);
        }
    } finally {
        if (requestId === state.detailRequestId) {
            state.detailLoading = false;
            hideSpeciesDetailLoading();
        }
    }
}

/* DETAIL LOADING UI */
function showSpeciesDetailLoading() {
    speciesDetailLoading?.classList.remove("hidden");
    speciesDetailError?.classList.add("hidden");

    if (!state.currentSpecies) {
        speciesDetailContent?.classList.add("hidden");
    }
}

function hideSpeciesDetailLoading() {
    speciesDetailLoading?.classList.add("hidden");
}

/* DETAIL RETRY */
function handleDetailRetry() {
    if (state.currentSpeciesName) {
        loadSpeciesDetail(state.currentSpeciesName);
    }
}

/* DETAIL ERROR */
function renderSpeciesDetailError(error) {
    speciesDetailError?.classList.remove("hidden");
    speciesDetailContent?.classList.add("hidden");

    const messageElement = document.getElementById(
        "species-detail-error-message"
    );

    if (!messageElement) {
        const errorText = speciesDetailError?.querySelector(".message-text");

        if (errorText) {
            errorText.textContent =
                error?.message === "SPECIES_NOT_FOUND"
                    ? "The requested species could not be found in the Society archive."
                    : "The species record could not be retrieved. Please check the archive service and try again.";
        }

        return;
    }

    messageElement.textContent =
        error?.message === "SPECIES_NOT_FOUND"
            ? "The requested species could not be found in the Society archive."
            : "The species record could not be retrieved. Please check the archive service and try again.";
}

/* GENERAL FORMATTING */
function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "0";
    }

    return new Intl.NumberFormat("en-US").format(number);
}

function formatMetadataValue(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "â€”";
    }

    return cleanText(String(value)) || "â€”";
}

function cleanText(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value).trim();
}

function normalizeNonNegativeInteger(value) {
    const number = Number(value);

    return Number.isFinite(number) && number > 0
        ? Math.floor(number)
        : 0;
}

/* SPECIES DETAIL RENDERING */
function renderSpeciesDetail(species, fromCache = false) {
    if (
        !species ||
        !species.identity ||
        typeof species.identity !== "object"
    ) {
        renderSpeciesDetailError(
            new Error("Invalid species record")
        );

        return;
    }

    if (!speciesDetailContent) {
        return;
    }

    speciesDetailError?.classList.add("hidden");
    speciesDetailContent.classList.remove("hidden");
    speciesDetailContent.replaceChildren();

    const fragment = document.createDocumentFragment();

    /*
     * Section order:
     * Identity
     * About
     * Biology
     * Classification
     * Names
     *
     * Media, People and Sources remain deferred until their
     * backend contracts are implemented.
     */
    const sections = [
        createIdentitySection(species.identity, species.names),
        createAboutSection(species.about),
        createBiologySection(species.biology),
        createClassificationSection(species.classification),
        createNamesSection(species.names)
    ];

    sections.filter(Boolean).forEach(section => {
        fragment.appendChild(section);
    });

    speciesDetailContent.appendChild(fragment);

    const identityHeading = speciesDetailContent.querySelector(
        ".identity-section > .detail-section-header > .detail-section-title"
    );

    if (identityHeading) {
        identityHeading.id = "species-detail-heading";
    }

    updateDetailCacheIndicator(fromCache);
    initializeExpandableSections();
}

/* CACHE INDICATOR */
function updateDetailCacheIndicator(fromCache) {
    document.getElementById("detail-cache-indicator")?.remove();

    if (!fromCache || !speciesDetailContent) {
        return;
    }

    const notice = document.createElement("p");
    notice.id = "detail-cache-indicator";
    notice.className = "detail-cache-indicator";
    notice.textContent = "Showing a locally cached record.";

    speciesDetailContent.prepend(notice);
}

/* SECTION FACTORY */
function createDetailSection(title, content, options = {}) {
    if (!content) {
        return null;
    }

    const section = document.createElement("section");
    section.className = "detail-section";

    if (options.className) {
        section.classList.add(options.className);
    }

    const header = document.createElement("header");
    header.className = "detail-section-header";

    const heading = document.createElement("h2");
    heading.className = "detail-section-title";
    heading.textContent = title;

    header.appendChild(heading);

    if (options.expandable) {
        const expanded = Boolean(options.expanded);

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "detail-section-toggle section-chevron";

        toggle.setAttribute("aria-expanded", String(expanded));
        toggle.classList.toggle("is-expanded", expanded);

        toggle.setAttribute(
            "aria-label",
            `${expanded ? "Collapse" : "Expand"} ${title}`
        );

        header.appendChild(toggle);

        section.dataset.expandable = "true";
        section.dataset.expanded = String(expanded);

        content.classList.add("detail-section-content");
        content.classList.toggle("section-collapsed", !expanded);
    }

    section.append(header, content);

    return section;
}

/* IDENTITY */
function createIdentitySection(identity, names) {
    if (!identity) {
        return null;
    }

    const content = document.createElement("div");
    content.className = "identity-content";

    const scientificName = document.createElement("p");
    scientificName.className = "record-scientific-name";
    scientificName.textContent = formatMetadataValue(
        identity.scientific_name
    );

    content.appendChild(scientificName);

    const authorshipText = cleanText(
        identity.scientific_name_authorship
    );

    if (authorshipText) {
        const authorship = document.createElement("p");
        authorship.className = "record-authorship";
        authorship.textContent = authorshipText;
        content.appendChild(authorship);
    }

    const metadata = document.createElement("dl");
    metadata.className = "record-metadata";

    appendDefinition(metadata, "Rank", identity.rank);

    appendDefinition(
        metadata,
        "Taxonomic status",
        identity.taxonomic_status
    );

    /*
     * English common names:
     * - Accept ISO 639-2 "eng" and ISO 639-1 "en".
     * - Ignore invalid or empty name records.
     * - Remove duplicate names while preserving their source order.
     * - Render one definition-list row with each name on its own line.
     * - Omit the row entirely if no English name exists.
     */
    const englishNames = Array.isArray(names)
        ? [
            ...new Set(
                names
                    .filter(nameRecord => {
                        if (
                            !nameRecord ||
                            typeof nameRecord !== "object"
                        ) {
                            return false;
                        }

                        const language = cleanText(
                            nameRecord.language
                        ).toLowerCase();

                        return (
                            (language === "eng" || language === "en") &&
                            Boolean(cleanText(nameRecord.name))
                        );
                    })
                    .map(nameRecord => cleanText(nameRecord.name))
            )
        ]
        : [];

    if (englishNames.length > 0) {
        const term = document.createElement("dt");
        term.textContent = "Common name (English)";

        const description = document.createElement("dd");

        englishNames.forEach(name => {
            const nameLine = document.createElement("div");
            nameLine.className = "common-name-english-entry";
            nameLine.textContent = name;

            description.appendChild(nameLine);
        });

        metadata.append(term, description);
    }

    if (metadata.children.length) {
        content.appendChild(metadata);
    }

    return createDetailSection("Identity", content, {
        className: "identity-section",
        expandable: true,
        expanded: true
    });
}

/* ABOUT */
function createAboutSection(about) {
    if (!about || typeof about !== "object") {
        return null;
    }

    const descriptionText = cleanText(about.description);
    const diet = cleanText(about.diet);
    const lifespan = cleanText(about.lifespan);
    const status = cleanText(about.status);

    if (!descriptionText && !diet && !lifespan && !status) {
        return null;
    }

    const content = document.createElement("div");
    content.className = "about-content";

    if (descriptionText) {
        const description = document.createElement("div");
        description.className = "record-description";

        appendParagraphs(description, descriptionText);

        content.appendChild(description);
    }

    const metadata = document.createElement("dl");
    metadata.className = "record-metadata";

    if (diet) {
        appendDefinition(metadata, "Diet", diet);
    }

    if (lifespan) {
        appendDefinition(metadata, "Lifespan", lifespan);
    }

    if (status) {
        appendDefinition(metadata, "Record status", status);
    }

    if (metadata.children.length) {
        content.appendChild(metadata);
    }

    return createDetailSection("About", content, {
        className: "about-section",
        expandable: true,
        expanded: false
    });
}

/* BIOLOGY */
function createBiologySection(biology) {
    if (
        !biology ||
        !Array.isArray(biology.traits) ||
        biology.traits.length === 0
    ) {
        return null;
    }

    const content = document.createElement("div");
    content.className = "biology-content";

    const groupedTraits = groupTraitsByCategory(biology.traits);

    Object.keys(groupedTraits)
        .sort((a, b) => a.localeCompare(b))
        .forEach(category => {
            const group = createTraitCategory(
                category,
                groupedTraits[category]
            );

            if (group) {
                content.appendChild(group);
            }
        });

    if (!content.children.length) {
        return null;
    }

    return createDetailSection("Biology", content, {
        className: "biology-section",
        expandable: true,
        expanded: true
    });
}

/* TRAIT GROUPING */
function groupTraitsByCategory(traits) {
    const groups = Object.create(null);

    traits.forEach(trait => {
        if (!trait || typeof trait !== "object") {
            return;
        }

        const category = cleanText(trait.category) || "General";

        if (!Object.prototype.hasOwnProperty.call(groups, category)) {
            groups[category] = [];
        }

        groups[category].push(trait);
    });

    return groups;
}

/* TRAIT CATEGORY */
function createTraitCategory(category, traits) {
    if (!Array.isArray(traits) || traits.length === 0) {
        return null;
    }

    const content = document.createElement("div");
    content.className =
        "trait-category-content detail-section-content";

    const list = document.createElement("div");
    list.className = "trait-observation-list";

    traits.forEach(trait => {
        const observation = createTraitRow(trait);

        if (observation) {
            list.appendChild(observation);
        }
    });

    if (!list.children.length) {
        return null;
    }

    content.appendChild(list);

    return createDetailSection(category, content, {
        className: "trait-category",
        expandable: true,
        expanded: false
    });
}

/* TRAIT ROW */
function createTraitRow(trait) {
    if (!trait || typeof trait !== "object") {
        return null;
    }

    const card = document.createElement("article");
    card.className = "trait-observation-card";

    const main = document.createElement("div");
    main.className = "trait-observation-main";

    const name = document.createElement("h4");
    name.className = "trait-name";
    name.textContent = formatMetadataValue(trait.trait);

    const value = document.createElement("p");
    value.className = "trait-value";
    value.textContent = formatTraitObservation(trait);

    main.append(name, value);
    card.appendChild(main);

    const sampleSize =
        trait.sample_size !== null &&
        trait.sample_size !== undefined &&
        trait.sample_size !== ""
            ? `n=${formatNumber(trait.sample_size)}`
            : "";

    const detailEntries = [
        ["Context", trait.context],
        ["Sample size", sampleSize],
        ["Source", trait.source],
        ["Source record", trait.source_record_id],
        ["Notes", trait.notes]
    ].filter(([, value]) => cleanText(value));

    if (detailEntries.length) {
        const details = document.createElement("details");
        details.className = "trait-provenance-details";

        const summary = document.createElement("summary");
        summary.textContent = "Observation details and source";
        details.appendChild(summary);

        const metadata = document.createElement("dl");
        metadata.className = "trait-provenance-list";

        detailEntries.forEach(([labelText, rawValue]) => {
            const term = document.createElement("dt");
            term.textContent = labelText;

            const description = document.createElement("dd");
            description.textContent =
                labelText === "Sample size"
                    ? rawValue
                    : cleanText(rawValue);

            metadata.append(term, description);
        });

        details.appendChild(metadata);
        card.appendChild(details);
    }

    return card;
}

/* TRAIT FORMATTING */
function formatTraitObservation(trait) {
    const numericValue = trait.value_numeric;
    const textValue = cleanText(trait.value_text);
    let observation = "â€”";

    if (
        numericValue !== null &&
        numericValue !== undefined &&
        numericValue !== ""
    ) {
        observation = formatNumberValue(numericValue);
    } else if (textValue) {
        observation = textValue;
    }

    const unit = cleanText(trait.unit);

    return unit ? `${observation} ${unit}` : observation;
}

function formatNumberValue(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return cleanText(String(value));
    }

    return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 6
    }).format(number);
}

function formatContext(trait) {
    const context = cleanText(trait?.context);
    const sampleSize = trait?.sample_size;

    if (
        !context &&
        (
            sampleSize === null ||
            sampleSize === undefined ||
            sampleSize === ""
        )
    ) {
        return "â€”";
    }

    const parts = [];

    if (context) {
        parts.push(context);
    }

    if (
        sampleSize !== null &&
        sampleSize !== undefined &&
        sampleSize !== ""
    ) {
        parts.push(`n=${formatNumber(sampleSize)}`);
    }

    return parts.join(" Â· ");
}


/* CLASSIFICATION */
function createClassificationSection(classification) {
    if (!classification || typeof classification !== "object") {
        return null;
    }

    const entries = [
        ["Kingdom", classification.kingdom],
        ["Phylum", classification.phylum],
        ["Class", classification.class_name],
        ["Order", classification.order],
        ["Family", classification.family],
        ["Genus", classification.genus],
        ["Specific epithet", classification.specific_epithet],
        ["Infraspecific epithet", classification.infraspecific_epithet]
    ].filter(([, value]) =>
        value !== null &&
        value !== undefined &&
        cleanText(String(value)) !== ""
    );

    if (!entries.length) {
        return null;
    }

    const content = document.createElement("div");
    content.className = "classification-content";

    const table = document.createElement("table");
    table.className = "classification-table";

    const colgroup = document.createElement("colgroup");

    const labelColumn = document.createElement("col");
    labelColumn.style.width = "145px";

    const valueColumn = document.createElement("col");

    colgroup.append(labelColumn, valueColumn);
    table.appendChild(colgroup);

    const caption = document.createElement("caption");
    caption.className = "visually-hidden";
    caption.textContent = "Taxonomic classification";
    table.appendChild(caption);

    const tbody = document.createElement("tbody");

    entries.forEach(([labelText, rawValue]) => {
        const row = document.createElement("tr");

        const label = document.createElement("th");
        label.scope = "row";
        label.textContent = labelText;

        const value = document.createElement("td");
        value.textContent = formatMetadataValue(rawValue);

        row.append(label, value);
        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    content.appendChild(table);

    return createDetailSection("Classification", content, {
        className: "classification-section",
        expandable: true,
        expanded: false
    });
}


/* VERNACULAR NAMES */
function createNamesSection(names) {
    if (!Array.isArray(names) || names.length === 0) {
        return null;
    }

    const content = document.createElement("div");
    content.className = "names-content";

    const list = document.createElement("ul");
    list.className = "vernacular-name-list";

    names.forEach(nameRecord => {
        if (!nameRecord || typeof nameRecord !== "object") {
            return;
        }

        const nameText = cleanText(nameRecord.name);

        if (!nameText) {
            return;
        }

        const item = document.createElement("li");
        item.className = "vernacular-name-item";

        const name = document.createElement("span");
        name.className = "vernacular-name";
        name.textContent = nameText;

        const language = document.createElement("span");
        language.className = "vernacular-language";
        language.textContent = formatLanguageCode(nameRecord.language);

        item.append(name, language);

        if (nameRecord.merged) {
            const merged = document.createElement("span");
            merged.className = "vernacular-merged";
            merged.textContent = "merged";
            item.appendChild(merged);
        }

        list.appendChild(item);
    });

    const nameItems = Array.from(list.children);

    if (!nameItems.length) {
        return null;
    }

    const summary = document.createElement("p");
    summary.className = "names-summary";
    summary.textContent =
        `${formatNumber(nameItems.length)} vernacular ` +
        `${nameItems.length === 1 ? "name" : "names"} recorded.`;

    content.append(summary, list);

    const initialNameLimit = 30;

    nameItems.forEach((item, index) => {
        if (index >= initialNameLimit) {
            item.classList.add("name-item-hidden");
        }
    });

    if (nameItems.length > initialNameLimit) {
        const moreButton = document.createElement("button");
        moreButton.type = "button";
        moreButton.className = "names-show-more";
        moreButton.textContent =
            `Show all ${formatNumber(nameItems.length)} names`;

        moreButton.setAttribute("aria-expanded", "false");

        moreButton.addEventListener("click", () => {
            const expanded =
                moreButton.getAttribute("aria-expanded") === "true";

            nameItems.forEach((item, index) => {
                if (index >= initialNameLimit) {
                    item.classList.toggle(
                        "name-item-hidden",
                        expanded
                    );
                }
            });

            moreButton.setAttribute(
                "aria-expanded",
                String(!expanded)
            );

            moreButton.textContent = expanded
                ? `Show all ${formatNumber(nameItems.length)} names`
                : "Show fewer names";
        });

        content.appendChild(moreButton);
    }

    return createDetailSection("Names", content, {
        className: "names-section",
        expandable: true,
        expanded: false
    });
}

/* LANGUAGE LABELS */
const LANGUAGE_LABELS = {
    eng: "English",
    zho: "Chinese",
    fra: "French",
    spa: "Spanish",
    msa: "Malay",
    ara: "Arabic",
    deu: "German",
    ita: "Italian",
    por: "Portuguese",
    rus: "Russian",
    jpn: "Japanese",
    kor: "Korean",
    hin: "Hindi",
    vie: "Vietnamese",
    tha: "Thai",
    ind: "Indonesian"
};

function formatLanguageCode(language) {
    const code = cleanText(language).toLowerCase();

    if (!code) {
        return "Unknown language";
    }

    return LANGUAGE_LABELS[code] || code.toUpperCase();
}

/* DEFINITION LIST HELPERS */
function appendDefinition(definitionList, label, value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return;
    }

    const term = document.createElement("dt");
    term.textContent = label;

    const description = document.createElement("dd");
    description.textContent = cleanText(String(value));

    definitionList.append(term, description);
}

/* TABLE HELPERS */
function appendTableHeader(row, text) {
    const header = document.createElement("th");
    header.scope = "col";
    header.textContent = text;
    row.appendChild(header);
}

/* DESCRIPTION PARAGRAPHS */
function appendParagraphs(container, text) {
    if (text === null || text === undefined || text === "") {
        return;
    }

    String(text)
        .split(/\n\s*\n/)
        .map(paragraph => paragraph.trim())
        .filter(Boolean)
        .forEach(paragraphText => {
            const paragraph = document.createElement("p");
            paragraph.textContent = paragraphText;
            container.appendChild(paragraph);
        });
}

/* EXPANDABLE SECTIONS */
function initializeExpandableSections() {
    if (!speciesDetailContent) {
        return;
    }

    speciesDetailContent
        .querySelectorAll("[data-expandable='true']")
        .forEach(section => {
            const toggle = section.querySelector(
                ":scope > .detail-section-header > .detail-section-toggle"
            );

            const heading = section.querySelector(
                ":scope > .detail-section-header > .detail-section-title"
            );

            if (!toggle) {
                return;
            }
            console.count("Expandable listener attached");

            toggle.addEventListener("click", () => {
                toggleExpandableSection(section, toggle);
            });

            if (heading) {
                heading.removeAttribute("role");
                heading.removeAttribute("tabindex");
                heading.removeAttribute("aria-expanded");
            }
        });
}

function toggleExpandableSection(section, toggle) {
    const newState = section.dataset.expanded !== "true";

    section.dataset.expanded = String(newState);

    toggle.setAttribute(
        "aria-expanded",
        String(newState)
    );

    toggle.textContent = "";
    toggle.classList.add("section-chevron");
    toggle.classList.toggle("is-expanded", newState);

    toggle.setAttribute(
        "aria-label",
        `${newState ? "Collapse" : "Expand"} ${getSectionTitle(section)}`
    );

    Array.from(section.children).forEach(child => {
        if (!child.classList.contains("detail-section-header")) {
            child.classList.toggle(
                "section-collapsed",
                !newState
            );
        }
    });
}

function getSectionTitle(section) {
    const title = section.querySelector(
        ":scope > .detail-section-header > .detail-section-title"
    );

    return title ? title.textContent : "section";
}
