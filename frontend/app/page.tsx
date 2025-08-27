"use client"
import { FileUpload } from "@/components/file-upload";
import Header from "@/components/header";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { Hexagon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";


export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
    if (!selectedFile) {
      return
    }
    toast.success(`file ${selectedFile?.name.replace(".csv", "")} was loaded!`)
  };

  const handleUpload = () => {
    if (!file) {
      toast.warning("Por favor, selecione um arquivo primeiro.");
      return;
    }

    setIsLoading(true);

  };

  
  return (
    <div className="space-y-8 bg-slate-50 dark:bg-slate-950">
      <Header />
      <div className="w-full text-center font-bold font-mono my-8">
        <h2 className="text-2xl">AI Data Processor - CSV</h2>
      </div>
      <div className="w-full max-w-lg h-screen mx-auto space-y-8">
        <FileUpload selectedFile={file} onFileSelect={handleFileChange}/>
        <Button 
          onClick={handleUpload} 
          disabled={!file || isLoading}
          className="w-full cursor-pointer bg-primary"
          size={"lg"} 
        >
        {isLoading ? "Enviando..." : "Enviar Arquivo"}
        </Button>
      </div>
    </div>
  );
}
