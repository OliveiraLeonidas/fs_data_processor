import { AlertCircle } from "lucide-react";
import { Progress } from "../ui/progress";

interface ProcessHeaderProps {
  completedCount: number;
  totalSteps: number | null;
  progressPercentage: number | null;
  error: string | null;
}

const ProcessHeader = ({
  completedCount,
  totalSteps,
  error,
  progressPercentage,
}: ProcessHeaderProps) => {
  return (
    <>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium text-slate-800 dark:text-slate-200">
            Progresso do Processamento
          </span>
          <span className="text-muted-foreground">
            {completedCount}/{totalSteps} etapas concluídas
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
    </>
  );
};

export default ProcessHeader;
