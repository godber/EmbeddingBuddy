from typing import Dict, List, Optional, Any, Tuple
import logging
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException


logger = logging.getLogger(__name__)


class OpenSearchClient:
    def __init__(self):
        self.client: Optional[OpenSearch] = None
        self.connection_info: Optional[Dict[str, Any]] = None

    def connect(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        verify_certs: bool = True,
    ) -> Tuple[bool, str]:
        """
        Connect to OpenSearch instance.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Parse URL to extract host and port
            if url.startswith("http://") or url.startswith("https://"):
                host = url
            else:
                host = f"https://{url}"

            # Build auth configuration
            auth_config = {}
            if username and password:
                auth_config["http_auth"] = (username, password)
            elif api_key:
                auth_config["api_key"] = api_key

            # Create client
            self.client = OpenSearch([host], verify_certs=verify_certs, **auth_config)

            # Test connection
            info = self.client.info()
            self.connection_info = {
                "url": host,
                "cluster_name": info.get("cluster_name", "Unknown"),
                "version": info.get("version", {}).get("number", "Unknown"),
            }

            return (
                True,
                f"Connected to {info.get('cluster_name', 'OpenSearch cluster')}",
            )

        except OpenSearchException as e:
            logger.error(f"OpenSearch connection error: {e}")
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error connecting to OpenSearch: {e}")
            return False, f"Unexpected error: {str(e)}"

    def get_index_mapping(self, index_name: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Get the mapping for a specific index.

        Returns:
            Tuple of (success: bool, mapping: Dict or None, message: str)
        """
        if not self.client:
            return False, None, "Not connected to OpenSearch"

        try:
            mapping = self.client.indices.get_mapping(index=index_name)
            return True, mapping, "Mapping retrieved successfully"
        except OpenSearchException as e:
            logger.error(f"Error getting mapping for index {index_name}: {e}")
            return False, None, f"Failed to get mapping: {str(e)}"

    def analyze_fields(self, index_name: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Analyze index fields to detect potential embedding and text fields.

        Returns:
            Tuple of (success: bool, analysis: Dict or None, message: str)
        """
        success, mapping, message = self.get_index_mapping(index_name)
        if not success:
            return False, None, message

        try:
            # Extract field information from mapping
            index_mapping = mapping[index_name]["mappings"]["properties"]

            analysis = {
                "vector_fields": [],
                "text_fields": [],
                "keyword_fields": [],
                "numeric_fields": [],
                "all_fields": [],
            }

            for field_name, field_info in index_mapping.items():
                field_type = field_info.get("type", "unknown")
                analysis["all_fields"].append(field_name)

                if field_type == "dense_vector":
                    analysis["vector_fields"].append(
                        {
                            "name": field_name,
                            "dimension": field_info.get("dimension", "unknown"),
                        }
                    )
                elif field_type == "text":
                    analysis["text_fields"].append(field_name)
                elif field_type == "keyword":
                    analysis["keyword_fields"].append(field_name)
                elif field_type in ["integer", "long", "float", "double"]:
                    analysis["numeric_fields"].append(field_name)

            return True, analysis, "Field analysis completed"

        except Exception as e:
            logger.error(f"Error analyzing fields: {e}")
            return False, None, f"Field analysis failed: {str(e)}"

    def fetch_sample_data(
        self, index_name: str, size: int = 5
    ) -> Tuple[bool, List[Dict], str]:
        """
        Fetch sample documents from the index.

        Returns:
            Tuple of (success: bool, documents: List[Dict], message: str)
        """
        if not self.client:
            return False, [], "Not connected to OpenSearch"

        try:
            response = self.client.search(
                index=index_name, body={"query": {"match_all": {}}, "size": size}
            )

            documents = [hit["_source"] for hit in response["hits"]["hits"]]
            return True, documents, f"Retrieved {len(documents)} sample documents"

        except OpenSearchException as e:
            logger.error(f"Error fetching sample data: {e}")
            return False, [], f"Failed to fetch sample data: {str(e)}"

    def fetch_data(
        self, index_name: str, size: int = 100
    ) -> Tuple[bool, List[Dict], str]:
        """
        Fetch documents from the index.

        Returns:
            Tuple of (success: bool, documents: List[Dict], message: str)
        """
        if not self.client:
            return False, [], "Not connected to OpenSearch"

        try:
            response = self.client.search(
                index=index_name, body={"query": {"match_all": {}}, "size": size}
            )

            documents = [hit["_source"] for hit in response["hits"]["hits"]]
            total_hits = response["hits"]["total"]["value"]

            message = f"Retrieved {len(documents)} documents from {total_hits} total"
            return True, documents, message

        except OpenSearchException as e:
            logger.error(f"Error fetching data: {e}")
            return False, [], f"Failed to fetch data: {str(e)}"

    def disconnect(self):
        """Disconnect from OpenSearch."""
        if self.client:
            self.client = None
            self.connection_info = None

    def is_connected(self) -> bool:
        """Check if connected to OpenSearch."""
        return self.client is not None
