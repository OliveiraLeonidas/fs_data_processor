"use client"

import React, { useCallback, useState } from 'react';
import { Upload, File, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn, formatBytes } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile?: File | null;
  disabled?: boolean;
}

export function FileUpload({ onFileSelect, selectedFile, disabled }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const csvFile = files.find(file => file.name.endsWith('.csv'));
    
    
    if (csvFile) {
      onFileSelect(csvFile);
    }
  }, [onFileSelect]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  const handleRemoveFile = () => {
    onFileSelect(null as never);
  };
console.log(selectedFile)
  return (
<Card className="w-full max-w-lg mx-auto">
      <CardContent className="p-6">
        {!selectedFile ? (
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-8 transition-colors text-center",
              isDragOver
                ? "border-blue-500 bg-blue-500/5"
                : "border-slate-300 hover:border-blue-500/50",
              disabled && "opacity-50 cursor-not-allowed"
            )}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileInputChange}
              disabled={disabled}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
            />
            
            <div className="flex flex-col items-center justify-center space-y-4">
              <Upload className={cn("h-12 w-12", isDragOver ? "text-blue-500" : "text-slate-400")} />
              <div className="space-y-2">
                <p className="text-lg font-medium text-slate-800">
                  {isDragOver ? "Solte o arquivo aqui" : "Selecione um arquivo CSV"}
                </p>
                <p className="text-sm text-slate-500">
                  Arraste e solte ou clique para selecionar
                </p>
              </div>
              <Button type="button" variant="outline" disabled={disabled}>
                Selecionar Arquivo
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between p-4 border rounded-lg bg-slate-50">
            <div className="flex items-center space-x-3 min-w-0">
              <File className="h-8 w-8 text-blue-600 flex-shrink-0" />
              <div className="min-w-0">
                <p className="font-medium text-sm truncate text-slate-800">{selectedFile.name}</p>
                <p className="text-xs text-slate-500">
                  {formatBytes(selectedFile.size)
                
                  }
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRemoveFile}
              disabled={disabled}
              aria-label="Remover arquivo"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );

  
}