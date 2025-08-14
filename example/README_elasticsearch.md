# Elasticsearch/OpenSearch Sample Data

This directory contains sample data files in Elasticsearch bulk index format for testing the OpenSearch integration in EmbeddingBuddy.

## Files

### Original NDJSON Files

- `sample_data.ndjson` - Original sample documents in EmbeddingBuddy format
- `sample_prompts.ndjson` - Original sample prompts in EmbeddingBuddy format

### Elasticsearch Bulk Files

- `sample_data_es_bulk.ndjson` - Documents in ES bulk format (index: "embeddings")
- `sample_prompts_es_bulk.ndjson` - Prompts in ES bulk format (index: "prompts")

## Usage

### 1. Index the data using curl

```bash
# Index main documents
curl -X POST "localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @sample_data_es_bulk.ndjson

# Index prompts
curl -X POST "localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @sample_prompts_es_bulk.ndjson
```

### 2. Create proper mappings (recommended)

First create the index with proper dense_vector mapping:

```bash
# Create embeddings index with dense_vector mapping
curl -X PUT "localhost:9200/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "index.knn": true
    },
    "mappings": {
      "properties": {
        "id": {"type": "keyword"},
        "embedding": {
          "type": "knn_vector",
          "dimension": 8,
          "method": {
            "engine": "lucene",
            "space_type": "cosinesimil",
            "name": "hnsw",
            "parameters": {}
          }
        },
        "text": {"type": "text"},
        "category": {"type": "keyword"},
        "subcategory": {"type": "keyword"},
        "tags": {"type": "keyword"}
      }
    }
  }'

# Create dense vector index with alternative field names
curl -X PUT "localhost:9200/prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "index.knn": true
    },
    "mappings": {
      "properties": {
        "id": {"type": "keyword"},
        "embedding": {
          "type": "knn_vector",
          "dimension": 8,
          "method": {
            "engine": "lucene",
            "space_type": "cosinesimil",
            "name": "hnsw",
            "parameters": {}
          }
        },
        "text": {"type": "text"},
        "category": {"type": "keyword"},
        "subcategory": {"type": "keyword"},
        "tags": {"type": "keyword"}
      }
    }
  }'
```

Then index the data using the bulk files above.

### 3. Test in EmbeddingBuddy

#### For "embeddings" index

- **OpenSearch URL**: `http://localhost:9200`
- **Index Name**: `embeddings`
- **Field Mapping**:
  - Embedding Field: `embedding`
  - Text Field: `text`
  - ID Field: `id`
  - Category Field: `category`
  - Subcategory Field: `subcategory`
  - Tags Field: `tags`

#### For "embeddings-dense" index (alternative field names)

- **OpenSearch URL**: `http://localhost:9200`
- **Index Name**: `embeddings-dense`
- **Field Mapping**:
  - Embedding Field: `vector`
  - Text Field: `content`
  - ID Field: `doc_id`
  - Category Field: `type`
  - Subcategory Field: `subtopic`
  - Tags Field: `keywords`

## Data Structure

### Original Format (from NDJSON files)

```json
{
  "id": "doc_001",
  "embedding": [0.2, -0.1, 0.8, 0.3, -0.5, 0.7, 0.1, -0.3],
  "text": "Machine learning algorithms are transforming healthcare...",
  "category": "technology",
  "subcategory": "healthcare",
  "tags": ["ai", "medicine", "prediction"]
}
```

### ES Bulk Format

```json
{"index": {"_index": "embeddings", "_id": "doc_001"}}
{"id": "doc_001", "embedding": [...], "text": "...", "category": "...", ...}
```

### Alternative Field Names (dense vector format)

```json
{"index": {"_index": "embeddings-dense", "_id": "doc_001"}}
{"doc_id": "doc_001", "vector": [...], "content": "...", "type": "...", ...}
```

## Notes

- All embedding vectors are 8-dimensional for these sample files
- The alternative format demonstrates how EmbeddingBuddy's field mapping handles different field names
- For production use, you may want larger embedding dimensions (e.g., 384, 768, 1536)
- The `dense_vector` field type in Elasticsearch/OpenSearch enables vector similarity search
