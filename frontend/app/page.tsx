"use client";

import { FileUpload } from "@/components/file-upload/file-upload";
import Header from "@/components/header";
import { ProgressSteps } from "@/components/progress-steps";
import { ResultsTable } from "@/components/results-table";
import { Separator } from "@/components/ui/separator";
import { apiClient } from "@/lib/api";
import { ResultResponse, StatusProcess, UploadResponse } from "@/types";
import { Bot, FileText } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const [uploadResponse, setUploadResponse] = useState<UploadResponse>();
  const [statusProcess, setStatusProcess] = useState<StatusProcess | null>(
    null
  );
  const [statusLoading, setStatusLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);

    if (!selectedFile && file) {
      toast.error(`Problem with the file you are trying to load`);
      setFile(null);
      return;
    }

    if (!selectedFile) {
      toast.error(`Problem with the file you are trying to load`);
      return;
    }

    if (selectedFile && !selectedFile?.name.endsWith(".csv")) {
      toast.error(`File must be a CSV file`);
      setFile(null);
      return;
    }

    toast.success(`file ${selectedFile?.name.replace(".csv", "")} was loaded!`);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.warning("Por favor, selecione um arquivo primeiro.");
      return;
    }
    setIsLoading(true);
    const response = await apiClient.uploadFile(file);

    if (!response) {
      toast.error("Error when try to upload file");
    }

    setUploadResponse(uploadResponse);
    toast.success(`File ${response.filename} with id: ${response.file_id}`);
    setIsLoading(false);
    setFile(null);
    fetchStatus(response.file_id);
    handleProcess(response.file_id);
  };

  const handleProcess = async (fileId: string) => {
    if (!fileId) {
      toast.error("File ID is required to process the file");
      return;
    }

    try {
      const response = await apiClient.processFile(fileId);

      if (!response) {
        toast.error(`No response when trying to process the file ${fileId}`);
        return;
      }

      toast.success(`${response.message}`);
      fetchStatus(fileId);
      handleExecute(fileId);
    } catch (e) {
      toast.error(`Error when trying to process the file - message: ${e}`);
    }
  };

  const handleExecute = async (fileId: string) => {
    if (!fileId) return;

    try {
      const response = await apiClient.executeScript(fileId);
      if (!response) {
        toast.error(`No response when trying to process the file ${fileId}`);
        return;
      }

      toast.success(
        `${response.message} - Processed Rows: ${response.processed_rows}`
      );
      fetchStatus(fileId);
      handleResult(fileId);
    } catch (e) {
      toast.error(`Error when trying to execute the script - message: ${e}`);
    }
  };

  const handleResult = async (fileId: string) => {
    if (!fileId) return;
    try {
      const response = await apiClient.results(fileId);
      if (!response) {
        toast.error("No response when trying to get the results");
      }

      setResult(response);
      fetchStatus(fileId);
    } catch (err) {
      toast.error(`Error when trying to get the results - message: ${err}`);
    }
  };

  const fetchStatus = async (fileId: string) => {
    if (!fileId) return;

    setStatusLoading(true);
    try {
      const status = await apiClient.getStatusProcess(fileId);
      setStatusProcess(status);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao buscar status");
    } finally {
      setStatusLoading(false);
    }
  };

  const handleDownload = async (file_id: string | undefined) => {
    if (!file_id) return;

    const response = apiClient.download(file_id);
    const blob = await response;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${file_id}_report_processed.csv`;
    a.click();

    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const cleanPage = () => {
    setFile(null);
    setResult(null);
    setStatusProcess(null);
    setError(null);
    setIsLoading(false);
    setStatusLoading(false);
    router.refresh();
  };
  return (
    <>
      <Header />
      <div className="space-y-8 px-16 py-12">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="relative">
              <Bot className="h-16 w-16 text-primary" />
              <div className="absolute -top-1 -right-1 bg-green-500 h-4 w-4 rounded-full flex items-center justify-center">
                <FileText className="h-2.5 w-2.5 text-white" />
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">
              AI CSV Cleaner
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Limpe e processe seus dados CSV automaticamente usando
              inteligência artificial
            </p>
          </div>
        </div>
        <div className="w-full space-y-8">
          <FileUpload
            selectedFile={file}
            onFileSelect={handleFileChange}
            upload={handleUpload}
            isUploading={isLoading}
          />
          {(statusProcess?.file_id || statusProcess) && (
            <>
              <div className="px-2 my-12">
                <Separator orientation="horizontal" />
              </div>
              <h2 className="text-xl text-muted-foreground">
                Etapa de Processamento
              </h2>
              <ProgressSteps
                statusProcess={statusProcess}
                error={error}
                isLoading={statusLoading}
              />
            </>
          )}

          {statusProcess?.ready && (
            <div className="">
              <div className="px-2 my-12">
                <Separator orientation="horizontal" />
              </div>
              <h2 className="text-xl text-muted-foreground pb-4 font-medium">
                Tabela com dados Processados
              </h2>
              <ResultsTable
                result={result}
                downloadFile={() => handleDownload(statusProcess?.file_id)}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
