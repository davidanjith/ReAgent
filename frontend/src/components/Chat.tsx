import { useState, useEffect, forwardRef, useImperativeHandle } from 'react'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

interface ChatProps {
  paperId?: string
  paperTitle?: string
}

export interface ChatHandle {
  sendMessage: (message: string) => Promise<void>
}

const Chat = forwardRef<ChatHandle, ChatProps>(({ paperId, paperTitle }, ref) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  useImperativeHandle(ref, () => ({
    sendMessage: async (message: string) => {
      if (!message.trim() || loading) return

      const userMessage: Message = {
        id: Date.now().toString(),
        content: message,
        role: 'user',
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMessage])
      setLoading(true)

      try {
        const response = await fetch('http://localhost:8000/chat/papers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: message,
            multi_doc: false,
          }),
        })

        if (!response.ok) {
          throw new Error('Chat request failed')
        }

        const data = await response.json()
        const assistantMessage: Message = {
          id: Date.now().toString(),
          content: data.response,
          role: 'assistant',
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
      } catch (error) {
        console.error('Chat error:', error)
        const errorMessage: Message = {
          id: Date.now().toString(),
          content: 'Sorry, I encountered an error. Please try again.',
          role: 'assistant',
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, errorMessage])
      } finally {
        setLoading(false)
      }
    },
  }))

  useEffect(() => {
    if (paperId && paperTitle) {
      // Add initial message when a paper is selected
      const initialMessage: Message = {
        id: Date.now().toString(),
        content: `I've loaded "${paperTitle}". What would you like to know about this paper?`,
        role: 'assistant',
        timestamp: new Date(),
      }
      setMessages([initialMessage])
    } else {
      setMessages([])
    }
  }, [paperId, paperTitle])

  return (
    <div className="flex h-[600px] flex-col bg-white shadow sm:rounded-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p className="mt-1 text-xs opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg bg-gray-100 px-4 py-2">
              <p className="text-sm text-gray-500">Thinking...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
})

Chat.displayName = 'Chat'

export default Chat 