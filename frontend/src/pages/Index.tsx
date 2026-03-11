import { useEffect, useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";

interface IndexProps {
  chat: any;
  updateChatMessages: (messages: any[]) => void;
  renameChat: (newTitle: string) => void;
}

const Index = ({ chat, updateChatMessages, renameChat }: IndexProps) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  useEffect(() => {
    if (uploadedFile) renameChat(uploadedFile.name.split(".")[0]);
  }, [uploadedFile]);

  return (
    <div className="min-h-screen bg-gradient-mesh">
      <div className="h-screen">
        <ChatInterface
          uploadedFile={uploadedFile}
          onFileUploaded={setUploadedFile}
          messages={chat?.messages || []}
          onMessagesChange={updateChatMessages}
        />
      </div>
    </div>
  );
};

export default Index;
