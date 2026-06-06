from .common import *

def get_skill_tools() -> List[Dict]:
    """
    Get tool definitions for the AI.
    These are passed to the API to register available tools.

    IMPORTANT: Search the skill as needed for the task, but avoid repeated
    searches for the same topic. Once you find the relevant API, provide the
    final response with Python code.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "Grep",
                "description": "Full-text search across files. Returns an aggregated summary (per-file hit counts + representative matches), not line-by-line results. Use after VectorSearch or when you know a specific API/pattern to confirm usage. For UI labels/actions, search slicer-ui-analysis/ when the UI pre-analysis has been built.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regex pattern to search for (e.g., 'loadVolume', 'downloadMRHead')"
                        },
                        "path": {
                            "type": "string",
                            "description": "Relative path within skill or virtual UI analysis root (e.g., 'slicer-source/Docs/developer_guide/script_repository', 'slicer-ui-analysis')"
                        }
                    },
                    "required": ["pattern", "path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "ReadFile",
                "description": "Read the content of a file from the skill knowledge base or generated UI analysis. For files under 500 lines, returns the full content. For larger files, provide a 'query' parameter to extract only relevant sections (e.g., the function or heading matching your keyword).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to file (e.g., 'slicer-source/Docs/developer_guide/script_repository/volumes.md', 'slicer-ui-analysis/Libs__MRML__Widgets__Resources__UI__qMRMLSliceControllerWidget.ui.md')"
                        },
                        "query": {
                            "type": "string",
                            "description": "Optional keyword to locate a specific section in large files (>500 lines). For markdown files, matches headings. For code files, matches function names or keywords."
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "VectorSearch",
                "description": "Dense vector search over the pre-indexed knowledge base, including generated UI-to-implementation analysis when built. Returns the most relevant code snippets. Use this as a fast first step before using ReadFile or Grep.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query describing what you need (e.g., 'load a volume and display it')"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top results to return (default 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
    ] + get_dynamic_extension_tools()
