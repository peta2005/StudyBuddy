import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, BookOpen, Upload } from "lucide-react";
import { UploadZone } from "@/components/UploadZone";
import { useToast } from "@/components/ui/use-toast"; // ✅ Added

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ page: number; excerpt: string }>;
}

interface ChatInterfaceProps {
  uploadedFile: File | null;
  onFileUploaded: (file: File) => void;
  messages: Message[];
  onMessagesChange: (messages: Message[]) => void;
}

export const ChatInterface = ({
  uploadedFile,
  onFileUploaded,
  messages,
  onMessagesChange,
}: ChatInterfaceProps) => {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const { toast } = useToast(); // ✅ Toast initialized

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    onMessagesChange([...messages, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer || "No response received from backend.",
        sources: data.sources || [],
      };

      onMessagesChange([...messages, userMessage, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const assistantMessage: Message = {
        role: "assistant",
        content: "⚠️ Server error. Check Flask backend.",
      };
      onMessagesChange([...messages, userMessage, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    onFileUploaded(file);
    setShowUpload(false);

    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        toast({
          title: "✅ Upload successful!",
          description: `"${file.name}" is ready for questions.`,
          duration: 3000,
        });
      } else {
        toast({
          title: "⚠️ Upload failed",
          description: "Please check your backend or try again.",
          variant: "destructive",
        });
      }
    } catch (err) {
      console.error("Upload error:", err);
      toast({
        title: "❌ Server error",
        description: "Could not connect to Flask backend.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      <div className="bg-card border-b border-border px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            {uploadedFile ? (
              <>
                <h2 className="font-semibold">{uploadedFile.name}</h2>
                <p className="text-sm text-muted-foreground">
                  Ask any question about your document
                </p>
              </>
            ) : (
              <>
                <h2 className="font-semibold">Smart Study Buddy</h2>
                <p className="text-sm text-muted-foreground">
                  Upload a document to get started
                </p>
              </>
            )}
          </div>
        </div>
        {uploadedFile && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowUpload(true)}
            className="gap-2"
          >
            <Upload className="w-4 h-4" />
            Change Document
          </Button>
        )}
      </div>

      <ScrollArea className="flex-1 p-6 space-y-6">
        {!uploadedFile || showUpload ? (
          <div className="text-center py-12 space-y-6">
            <UploadZone onFileUploaded={handleFileUpload} />
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 ${
                  message.role === "user"
                    ? "bg-gradient-primary text-primary-foreground shadow-soft"
                    : "bg-card border border-border shadow-soft"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-card border border-border rounded-2xl p-4 shadow-soft">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-primary rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-2 h-2 bg-primary rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        )}
      </ScrollArea>

      <div className="border-t border-border p-6">
        <div className="flex gap-3">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder={
              uploadedFile
                ? "Ask a question about your document..."
                : "Upload a document first..."
            }
            className="flex-1 h-12 rounded-xl border-2"
            disabled={isLoading || !uploadedFile}
          />
          <Button
            onClick={handleSend}
            disabled={isLoading || !input.trim() || !uploadedFile}
            size="lg"
            className="bg-gradient-primary hover:shadow-glow px-6"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};
