'use client';

import React from 'react';
import { Check, Loader2, AlertCircle, Upload, Brain, Play, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { StatusProcess } from '@/types';
import { cn } from '@/lib/utils';

interface ProgressStepsProps {
  statusProcess: StatusProcess | null;
  isLoading?: boolean;
  error?: string | null;
}

export function ProgressSteps({ 
  statusProcess, 
  isLoading = false, 
  error = null
}: ProgressStepsProps) {
  
  const steps = [
    {
      title: 'Upload',
      description: 'Arquivo enviado para o servidor',
      icon: Upload,
      completed: statusProcess?.uploaded || false,
      processing: statusProcess && !statusProcess.uploaded
    },
    {
      title: 'Processado pela LLM',
      description: 'IA analisando e gerando script de limpeza',
      icon: Brain,
      completed: statusProcess?.processed_by_llm || false,
      processing: statusProcess?.uploaded && !statusProcess.processed_by_llm
    },
    {
      title: 'Script Executado',
      description: 'Transformações aplicadas nos dados',
      icon: Play,
      completed: statusProcess?.script_executed || false,
      processing: statusProcess?.processed_by_llm && !statusProcess.script_executed
    },
    {
      title: 'Resposta Devolvida',
      description: 'Dados processados disponíveis para o usuário',
      icon: CheckCircle,
      completed: statusProcess?.ready || false,
      processing: statusProcess?.script_executed && !statusProcess.ready
    }
  ];

  const completedCount = steps.filter(step => step.completed).length;
  const progressPercentage = (completedCount / steps.length) * 100;

  const getIcon = (step: typeof steps[0], index: number) => {
    const IconComponent = step.icon;
    
    if (error && step.processing) {
      return <AlertCircle className="h-5 w-5 text-red-600" />;
    }
    if (step.completed) {
      return <Check className="h-5 w-5 text-green-600" />;
    }
    if (step.processing) {
      return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
    }
    return <IconComponent className="h-5 w-5 text-muted-foreground" />;
  };

  const getStepColor = (step: typeof steps[0]) => {
    if (error && step.processing) return 'text-red-600 dark:text-red-400';
    if (step.completed) return 'text-green-600 dark:text-green-400';
    if (step.processing) return 'text-blue-600 dark:text-blue-400';
    return 'text-muted-foreground';
  };

  const getStepBorder = (step: typeof steps[0]) => {
    if (error && step.processing) return 'border-red-200 dark:border-red-800 bg-red-50/50 dark:bg-red-950/20';
    if (step.completed) return 'border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20';
    if (step.processing) return 'border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/20';
    return 'border-muted-foreground/20';
  };

  //TODO: convert to component and reuse stepItem
  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* step header */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-slate-800 dark:text-slate-200">
                Progresso do Processamento
              </span>
              <span className="text-muted-foreground">
                {completedCount}/{steps.length} etapas concluídas
              </span>
            </div>
            <Progress value={progressPercentage} className="h-2" />
            {error && (
              <div className="flex items-center space-x-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}
          </div>
            {/* TODO: step item */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {index < steps.length - 1 && (
                  <div className="absolute left-6 top-12 w-0.5 h-8 bg-muted-foreground/20" />
                )}
                
                <div className={cn(
                  "flex items-start space-x-4 p-4 rounded-lg border transition-all duration-200",
                  getStepBorder(step)
                )}>
                  <div className="flex-shrink-0 mt-0.5">
                    {getIcon(step, index)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={cn("font-semibold text-sm", getStepColor(step))}>
                          {step.title}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {step.description}
                        </p>
                      </div>
                      
                      <div className="flex-shrink-0 ml-4">
                        {error && step.processing && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300">
                            Erro
                          </span>
                        )}
                        {!error && step.processing && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                            Em andamento...
                          </span>
                        )}
                        {step.completed && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                            Concluído
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

            {/* TODO: step footer */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {isLoading && <Loader2 className="h-4 w-4 animate-spin text-blue-600" />}
                <span className={cn(
                  "text-sm font-medium",
                  statusProcess?.ready && "text-green-600 dark:text-green-400",
                  error && "text-red-600 dark:text-red-400",
                  !statusProcess?.ready && !error && "text-muted-foreground"
                )}>
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