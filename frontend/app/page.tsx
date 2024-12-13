import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { UrlForm } from "@/components/url-form"

export default function Home() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">URL to Podcast Converter</h1>
      <UrlForm />
    </main>
  )
}
