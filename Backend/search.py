import os
import hashlib
import httpx
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField, SearchFieldDataType
from azure.core.credentials import AzureKeyCredential

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
SEARCH_KEY      = os.getenv("AZURE_SEARCH_KEY", "")
SEARCH_INDEX    = os.getenv("AZURE_SEARCH_INDEX", "travelai-guides")


def _credential():
    """Returns the Azure key credential used to authenticate with the search service."""
    return AzureKeyCredential(SEARCH_KEY)


def ensure_index():
    """Create the Azure AI Search index if it doesn't already exist."""
    client = SearchIndexClient(SEARCH_ENDPOINT, _credential())
    existing = [idx.name for idx in client.list_indexes()]
    if SEARCH_INDEX in existing:
        return
    index = SearchIndex(
        name=SEARCH_INDEX,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="destination", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
        ],
    )
    client.create_index(index)
    print(f"[Search] created index: {SEARCH_INDEX}")

# creates the index for a deestination by fetching wikivoyage
def fetch_wikivoyage(destination: str) -> str:
    """Fetch the plain-text travel guide for a destination from the Wikivoyage API.
    Returns the guide text, or an empty string if nothing is found."""
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(
                "https://en.wikivoyage.org/w/api.php",
                params={
                    "action": "query",
                    "titles": destination,
                    "prop": "extracts",
                    "format": "json",
                    "explaintext": "1",
                    "exsectionformat": "plain",
                },
            )
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            extract = page.get("extract", "")
            if extract:
                return extract[:8000]  # cap to avoid bloating the AI prompt
    except Exception as e:
        print(f"[Search] Wikivoyage fetch failed: {e}")
    return ""


def index_destination(destination: str):
    """Fetch Wikivoyage content for a destination and upsert it into the Azure AI Search index.
    Safe to call multiple times — will overwrite the existing document for that destination."""
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        print("[Search] skipping — no Azure Search credentials")
        return

    ensure_index()

    content = fetch_wikivoyage(destination)
    if not content:
        print(f"[Search] no Wikivoyage content found for: {destination}")
        return

    # use a hash of the destination name as a stable unique document id
    doc_id = hashlib.md5(destination.lower().encode()).hexdigest()

    search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, _credential())
    search_client.upload_documents([{"id": doc_id, "destination": destination, "content": content}])
    print(f"[Search] indexed: {destination}")


def search_destination(destination: str, query: str) -> str:
    """Search the index for travel guide content relevant to this destination and query.
    Returns the top result's content as a string, or empty string if nothing found."""
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        return ""
    try:
        search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, _credential())
        results = search_client.search(
            search_text=f"{destination} {query}",
            filter=f"destination eq '{destination}'",
            top=1,
        )
        for result in results:
            content = result.get("content", "")
            print(f"[Search] found context for {destination} ({len(content)} chars)")
            return content[:3000]
    except Exception as e:
        print(f"[Search] search failed: {e}")
    return ""
