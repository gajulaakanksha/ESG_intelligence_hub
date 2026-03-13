from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def perform_web_search(query):
    """
    Perform a live web search using DuckDuckGo.
    Returns the search results as a string.
    """
    try:
        # Using the wrapper to get more detailed results if needed
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
        search = DuckDuckGoSearchRun(api_wrapper=wrapper)
        
        results = search.run(query)
        return results
    except Exception as e:
        print(f"Error performing web search: {str(e)}")
        return "Search failed. Please try again later."

def get_search_tool():
    """Returns a DuckDuckGo search tool object for manual usage"""
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=3)
        return DuckDuckGoSearchRun(api_wrapper=wrapper)
    except:
        return None
