'use client'

import { useState, useRef } from 'react'
import { MagnifyingGlassIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import Chat from '@/components/Chat'

interface Paper {
  id: string
  title: string
  abstract: string
  authors: string[]
  year: number
  url: string
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null)
  const [message, setMessage] = useState('')
  const chatRef = useRef<{ sendMessage: (message: string) => Promise<void> }>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setSelectedPaper(null)

    try {
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

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const data = await response.json()
      setPapers(data.papers)
    } catch (err) {
      setError('Failed to fetch papers. Please try again.')
      console.error('Search error:', err)
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
        <div className="bg-white shadow sm:rounded-lg">
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
          {papers.map((paper) => (
            <div
              key={paper.id}
              className={`bg-white shadow sm:rounded-lg overflow-hidden cursor-pointer transition-colors ${
                selectedPaper?.id === paper.id ? 'ring-2 ring-indigo-600' : 'hover:bg-gray-50'
              }`}
              onClick={() => setSelectedPaper(paper)}
            >
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  {paper.title}
                </h3>
                <div className="mt-2 text-sm text-gray-500">
                  <p className="font-medium">Authors: {paper.authors.join(', ')}</p>
                  <p className="mt-1">{paper.abstract}</p>
                </div>
                <div className="mt-4">
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View Paper <span aria-hidden="true">&rarr;</span>
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-base font-semibold leading-6 text-gray-900">
              Chat with AI Assistant
            </h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>
                {selectedPaper
                  ? `Ask questions about "${selectedPaper.title}"`
                  : 'Select a paper to start chatting about it'}
              </p>
            </div>
          </div>
        </div>

        <Chat
          ref={chatRef}
          paperId={selectedPaper?.id}
          paperTitle={selectedPaper?.title}
        />

        {selectedPaper && (
          <form onSubmit={handleSendMessage} className="bg-white shadow sm:rounded-lg p-4">
            <div className="flex space-x-3">
              <input
                type="text"
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
