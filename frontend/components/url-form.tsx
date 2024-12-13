'use client'

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { API_URL } from "@/lib/config"  // Add this import

export function UrlForm() {
  const [url, setUrl] = useState("")
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setContent(null)

    try {
      const response = await fetch(`${API_URL}/api/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch content')
      }

      const data = await response.json()
      setContent(data.content)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="space-y-4">
        <Input 
          type="url" 
          placeholder="Enter article URL..." 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? 'Converting...' : 'Convert to Audio'}
        </Button>
      </form>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {content && (
        <Card>
          <CardContent className="pt-6">
            <div className="prose prose-sm max-w-none">
              {content.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}