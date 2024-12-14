import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Check, Copy } from "lucide-react";

const CopyFeedButton = () => {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();
  const feedUrl = "https://d3okqvlrlpcnz0.cloudfront.net/feed.xml";

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(feedUrl);
      setCopied(true);
      toast({
        title: "Copied!",
        description: "Podcast feed URL copied to clipboard",
        duration: 2000
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
      toast({
        title: "Failed to copy",
        description: "Please try again",
        variant: "destructive"
      });
    }
  };

  return (
    <Button
      onClick={copyToClipboard}
      className="w-full mt-4 gap-2"
      variant="outline"
    >
      {copied ? (
        <>
          <Check className="w-4 h-4" />
          Copied Feed URL
        </>
      ) : (
        <>
          <Copy className="w-4 h-4" />
          Copy Podcast Feed URL
        </>
      )}
    </Button>
  );
};

export default CopyFeedButton;