"""
LLM Response Caching Module

This module provides caching functionality for LLM responses to improve performance
and reduce API costs for repeated queries.
"""

import hashlib
import json
import os
import time
from functools import wraps
from typing import Callable, Any

# Cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def cache_llm_response(func: Callable) -> Callable:
    """
    Decorator to cache LLM responses to disk

    Caches responses by hashing the prompt. Speeds up repeated generations
    with identical inputs by 90%+.

    Args:
        func: The LLM call function to cache

    Returns:
        Wrapped function with caching capability
    """
    @wraps(func)
    def wrapper(prompt: str, *args, **kwargs) -> str:
        # Create hash of prompt for cache key
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{prompt_hash}.json")

        # Check if response is cached
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    print(f"[CACHE HIT] Using cached response for prompt hash: {prompt_hash[:8]}...")
                    return cached_data['response']
            except Exception as e:
                print(f"Cache read error: {e}")
                # If cache read fails, continue to call LLM

        # Call LLM if not cached or cache read failed
        print(f"[CACHE MISS] Calling LLM for new prompt...")
        response = func(prompt, *args, **kwargs)

        # Save response to cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'prompt_preview': prompt[:200],  # Store partial prompt for debugging
                    'response': response,
                    'timestamp': time.time(),
                    'prompt_hash': prompt_hash
                }, f, ensure_ascii=False, indent=2)
            print(f"[CACHE SAVED] Response cached with hash: {prompt_hash[:8]}...")
        except Exception as e:
            print(f"Cache write error: {e}")
            # Cache write failure doesn't affect the response

        return response

    return wrapper


def clear_cache() -> None:
    """Clear all cached responses"""
    import shutil
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)
        print("Cache cleared successfully")


def get_cache_stats() -> dict:
    """
    Get cache statistics

    Returns:
        Dictionary with cache statistics
    """
    if not os.path.exists(CACHE_DIR):
        return {
            'total_cached_items': 0,
            'cache_size_mb': 0,
            'oldest_cache_timestamp': None,
            'newest_cache_timestamp': None
        }

    cache_files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.json')]
    total_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in cache_files)

    timestamps = []
    for cache_file in cache_files:
        try:
            with open(os.path.join(CACHE_DIR, cache_file), 'r') as f:
                data = json.load(f)
                timestamps.append(data.get('timestamp', 0))
        except:
            pass

    return {
        'total_cached_items': len(cache_files),
        'cache_size_mb': round(total_size / (1024 * 1024), 2),
        'oldest_cache_timestamp': min(timestamps) if timestamps else None,
        'newest_cache_timestamp': max(timestamps) if timestamps else None
    }
