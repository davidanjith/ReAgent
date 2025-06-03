'use client'

import { useState, useRef } from 'react'
import { MagnifyingGlassIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import Chat from '@/components/Chat'

interface Paper {
  paper_id: string
  title: string
  abstract: string
  authors: string[]
  year: number
  url: string
  pdf_url?: string
  summary?: string
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTabId, setActiveTabId] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const chatRef = useRef<{ sendMessage: (message: string) => Promise<void> }>(null)
  const [collectiveSummary, setCollectiveSummary] = useState<string>('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')

    try {
      console.log('Making search request with query:', query)
      const response = await fetch('http://localhost:8000/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          max_results: 5,
        }),
      })

      console.log('Search response status:', response.status)
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error(`Search failed: ${errorText}`)
      }

      console.log('Waiting for response data...')
      const data = await response.json()
      console.log('Search response data:', data)
      
      if (!data.papers || !Array.isArray(data.papers)) {
        console.error('Invalid response format:', data)
        throw new Error('Invalid response format from server')
      }

      console.log(`Received ${data.papers.length} papers`)
      const papersWithSummaries = data.papers.map((paper: Paper) => ({ ...paper, summary: paper.summary || 'No summary available.' }))
      console.log('Papers with summaries:', papersWithSummaries)
      setPapers(papersWithSummaries)
      setCollectiveSummary(data.summary || '')
      if (papersWithSummaries.length > 0) {
        setActiveTabId(papersWithSummaries[0].paper_id)
      } else if (data.summary) {
        setActiveTabId('collective-summary')
      } else {
        setActiveTabId(null)
      }
    } catch (err) {
      console.error('Search error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch papers. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || !chatRef.current) return

    await chatRef.current.sendMessage(message)
    setMessage('')
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-6">
        {/* Research Paper Search Card */}
        <div className="bg-white shadow-md border border-gray-200 sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              Research Paper Search
            </h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>Enter your research query to find relevant papers.</p>
            </div>
            <form onSubmit={handleSearch} className="mt-5 sm:flex sm:items-center">
              <div className="w-full sm:max-w-xs">
                <label htmlFor="search" className="sr-only">
                  Search
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </div>
                  <input
                    type="text"
                    name="search"
                    id="search"
                    className="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    placeholder="Enter your research query"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="mt-3 inline-flex w-full items-center justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:ml-3 sm:mt-0 sm:w-auto"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </form>
          </div>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {/* Papers Tab Bar */}
          {papers.length > 0 && (
            <div className="bg-white border-b border-gray-200 rounded-t-lg">
              <nav className="-mb-px flex space-x-8 overflow-x-auto px-4" aria-label="Tabs">
                {papers.map((paper, index) => (
                  <button
                    key={`${paper.paper_id}-${index}`}
                    onClick={() => setActiveTabId(paper.paper_id)}
                    className={`
                      whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm bg-white
                      ${activeTabId === paper.paper_id
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-600 hover:text-gray-800'
                      }
                    `}
                  >
                    {paper.title.length > 30 ? paper.title.substring(0, 30) + '...' : paper.title}
                  </button>
                ))}
              </nav>
            </div>
          )}

          {/* Papers Content */}
          {papers.length > 0 ? (
            activeTabId ? (
              // Show selected paper
              <div className="space-y-4">
                {(() => {
                  const paper = papers.find(p => p.paper_id === activeTabId);
                  if (!paper) return null;
                  
                  return (
                    <>
                      {/* Paper Details Card */}
                      <div className="bg-white shadow-md border border-gray-200 rounded-lg overflow-hidden">
                        <div className="p-6">
                          <div className="mb-4">
                            <span className="text-sm font-medium text-indigo-600">
                              {paper.year}
                            </span>
                          </div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            {paper.title}
                          </h3>
                          <div className="space-y-3">
                            <p className="text-sm text-gray-600">
                              {paper.authors.map((author, i) => (
                                <span key={`${paper.paper_id}-author-${i}`}>
                                  {author}{i < paper.authors.length - 1 ? ', ' : ''}
                                </span>
                              ))}
                            </p>
                            <p className="text-sm text-gray-500">
                              {paper.abstract}
                            </p>
                          </div>
                          <div className="mt-4 flex justify-end">
                            <a
                              href={paper.pdf_url || paper.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
                              onClick={(e) => e.stopPropagation()}
                            >
                              View Paper <span aria-hidden="true" className="ml-1">&rarr;</span>
                            </a>
                          </div>
                        </div>
                      </div>

                      {/* Individual Paper Summary Card */}
                      {paper.summary && paper.summary !== 'No summary available.' && (
                        <div className="bg-white shadow-md border border-gray-200 rounded-lg overflow-hidden mt-4">
                          <div className="p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
                            <p className="text-sm text-gray-700">{paper.summary}</p>
                          </div>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            ) : (
              // Show message when no paper is selected
              <div className="bg-white shadow-md border border-gray-200 rounded-lg p-6 text-center text-gray-500">
                Select a paper from the tabs above to view details
              </div>
            )
          ) : (
            // Show message when no papers are found
            <div className="bg-white shadow-md border border-gray-200 rounded-lg p-6 text-center text-gray-500">
              No papers found. Try a different search query.
            </div>
          )}

          {/* Collective Summary Card (if it exists) */}
          {collectiveSummary && (
            <div className="bg-white shadow-md border border-gray-200 rounded-lg overflow-hidden mt-4">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary of Search Results</h3>
                <p className="text-sm text-gray-700">{collectiveSummary}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {/* Chat with AI Assistant Info Card */}
        <div className="bg-white shadow-md border border-gray-200 sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              Chat with AI Assistant
            </h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>
                {activeTabId
                  ? `Ask questions about "${papers.find(p => p.paper_id === activeTabId)?.title}"`
                  : 'Select a paper to start chatting about it'}
              </p>
            </div>
          </div>
        </div>

        <Chat
          ref={chatRef}
          paperId={activeTabId === 'collective-summary' ? undefined : activeTabId || undefined}
          paperTitle={activeTabId === 'collective-summary' ? undefined : papers.find(p => p.paper_id === activeTabId)?.title}
          paperAbstract={activeTabId === 'collective-summary' ? undefined : papers.find(p => p.paper_id === activeTabId)?.abstract}
        />

        {/* Chat Input Form */}
        {activeTabId !== 'collective-summary' && activeTabId && (
          <form onSubmit={handleSendMessage} className="bg-white shadow-md border border-gray-200 sm:rounded-lg p-4">
            <div className="flex space-x-3">
              <input
                type="text"
                id="chat-message-input"
                name="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              />
              <button
                type="submit"
                disabled={!message.trim()}
                className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PaperAirplaneIcon className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
