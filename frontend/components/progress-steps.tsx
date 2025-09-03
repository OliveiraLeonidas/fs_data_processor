"use client";

import React from "react";
import { Loader2, Upload, Brain, Play, CheckCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { StatusProcess } from "@/types";
import { cn } from "@/lib/utils";
import ProcessHeader from "./steps/process-header";
import { ProcessItem } from "./steps/step-item";

interface ProgressStepsProps {
  statusProcess: StatusProcess | null;
  isLoading?: boolean;
  error?: string | null;
}

export function ProgressSteps({
  statusProcess,
  isLoading = false,
  error = null,
}: ProgressStepsProps) {
  const steps = [
    {
      title: "Upload",
      description: "Arquivo enviado para o servidor",
      icon: Upload,
      completed: !!statusProcess?.uploaded || false,
      processing: !!statusProcess && !statusProcess.uploaded,
    },
    {
      title: "Processado pela LLM",
      description: "IA analisando e gerando script de limpeza",
      icon: Brain,
      completed: !!statusProcess?.processed_by_llm || false,
      processing: !!statusProcess?.uploaded && !statusProcess.processed_by_llm,
    },
    {
      title: "Script Executado",
      description: "Transformações aplicadas nos dados",
      icon: Play,
      completed: !!statusProcess?.script_executed || false,
      processing:
        !!statusProcess?.processed_by_llm && !statusProcess.script_executed,
    },
    {
      title: "Resposta Devolvida",
      description: "Dados processados disponíveis para o usuário",
      icon: CheckCircle,
      completed: !!statusProcess?.ready || false,
      processing: !!statusProcess?.script_executed && !statusProcess.ready,
    },
  ];

  const completedCount = steps.filter((step) => step.completed).length;
  const progressPercentage = (completedCount / steps.length) * 100;

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <div className="space-y-6">
          <ProcessHeader
            completedCount={completedCount}
            totalSteps={steps.length}
            error={error}
            progressPercentage={progressPercentage}
          />

          <div className="space-y-4">
            {steps.map((step, index) => (
              <ProcessItem
                key={step.title}
                step={step}
                index={index}
                isLast={index === steps.length - 1}
                error={error}
              />
            ))}
          </div>

          {/* TODO: step footer */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isLoading && (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                )}
                <span
                  className={cn(
                    "text-sm font-medium",
                    statusProcess?.ready &&
                      "text-green-600 dark:text-green-400",
                    error && "text-red-600 dark:text-red-400",
                    !statusProcess?.ready && !error && "text-muted-foreground"
                  )}
                >
                  {statusProcess?.ready
                    ? "Processamento concluído com sucesso!"
                    : error
                    ? "Erro no processamento"
                    : isLoading
                    ? "Verificando status..."
                    : "Aguardando início do processamento"}
                </span>
              </div>

              {statusProcess && (
                <div className="text-xs text-muted-foreground">
                  File ID: {statusProcess.file_id.substring(0, 8)}...
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
