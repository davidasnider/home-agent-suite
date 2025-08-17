"""
Test query data for Google Search Agent testing.

This module contains various test queries and expected behaviors
for comprehensive testing scenarios.
"""

# Basic search queries
BASIC_QUERIES = [
    "weather today",
    "latest news",
    "python programming tutorial",
    "machine learning basics",
    "healthy recipes",
]

# Complex search queries
COMPLEX_QUERIES = [
    "How to implement machine learning algorithms in Python for beginners",
    "What are the best practices for REST API design in 2024",
    "Climate change impact on renewable energy adoption worldwide",
    "Artificial intelligence ethics and responsible AI development",
]

# Edge case queries
EDGE_CASE_QUERIES = [
    "",  # Empty query
    " ",  # Whitespace only
    "a",  # Single character
    "123456789",  # Numbers only
    "!@#$%^&*()",  # Special characters only
    "query with\nnewlines\tand\ttabs",  # Special whitespace
    "very " * 50 + "long query",  # Very long query  # pragma: allowlist secret
]

# Queries that typically return no results
NO_RESULTS_QUERIES = [
    "asdfghjklqwertyuiopzxcvbnm12345",  # pragma: allowlist secret
    "nonexistent_term_99999",
    "zzzzz_impossible_search_term_zzzzz",
]

# Queries for testing specific domains
DOMAIN_SPECIFIC_QUERIES = [
    "site:github.com python machine learning",
    "site:stackoverflow.com javascript error handling",
    "site:reddit.com best programming books",
]

# Queries with different intents
INTENT_BASED_QUERIES = {
    "informational": [
        "what is artificial intelligence",
        "how does photosynthesis work",
        "history of the internet",
    ],
    "navigational": ["github login", "google maps", "youtube"],
    "transactional": [
        "buy python programming books",
        "download visual studio code",
        "subscribe to newsletter",
    ],
    "research": [
        "compare machine learning frameworks",
        "best practices for software architecture",
        "renewable energy statistics 2024",
    ],
}

# Expected query processing behaviors
QUERY_EXPECTATIONS = {
    "empty_query": {"should_fail": True, "expected_error": "Invalid or empty query"},
    "normal_query": {"should_fail": False, "min_results": 0, "max_results": 10},
    "long_query": {"should_fail": False, "should_truncate": True, "max_length": 500},
}

# Mock responses for specific queries
QUERY_MOCK_RESPONSES = {
    "weather today": "successful_weather_search",
    "latest technology": "successful_tech_search",
    "nonexistent_query": "empty_search_results",
    "quota_test": "api_quota_error",
    "timeout_test": "network_timeout_error",
    "invalid_test": "invalid_query_error",
    "auth_test": "api_key_error",
    "partial_test": "partial_response",
    "large_test": "large_response",
    "malformed_test": "malformed_response",
}
