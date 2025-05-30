import pytest
from core_agent.summary_pipeline import summarize_topic

def test_summarize_topic_valid_input():
    """Test summarize_topic with valid input"""
    # Test with a specific research topic
    result = summarize_topic("quantum computing applications in machine learning")
    
    # Verify the structure of the response
    assert isinstance(result, dict)
    assert "keywords" in result
    assert "papers" in result
    assert "summary" in result
    
    # Verify the content
    assert isinstance(result["keywords"], list)
    assert len(result["keywords"]) > 0
    assert isinstance(result["papers"], list)
    assert isinstance(result["summary"], str)
    
    # Verify no error in successful case
    assert "error" not in result

def test_summarize_topic_empty_input():
    """Test summarize_topic with empty input"""
    with pytest.raises(ValueError):
        summarize_topic("")

def test_summarize_topic_invalid_input():
    """Test summarize_topic with invalid input type"""
    with pytest.raises(ValueError):
        summarize_topic(None)

def test_summarize_topic_max_papers():
    """Test summarize_topic with max_papers parameter"""
    max_papers = 3
    result = summarize_topic(
        "artificial intelligence in healthcare",
        max_papers=max_papers
    )
    
    assert len(result["papers"]) <= max_papers

def test_summarize_topic_no_results():
    """Test summarize_topic with a topic that might not have papers"""
    result = summarize_topic("xyz123nonexistenttopic")
    
    assert "error" in result
    assert "No papers found" in result["error"]
    assert len(result["papers"]) == 0
    assert result["summary"] == ""

if __name__ == "__main__":
    # Run tests manually if needed
    test_summarize_topic_valid_input()
    test_summarize_topic_empty_input()
    test_summarize_topic_invalid_input()
    test_summarize_topic_max_papers()
    test_summarize_topic_no_results()
    print("All tests passed!") 