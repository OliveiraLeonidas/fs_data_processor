import { cn } from "@/lib/utils";
import { AlertCircle, Check, Loader2 } from "lucide-react";
import { Badge } from "../ui/badge";

interface StepItemProps {
  step: {
    title: string;
    description: string;
    icon: React.ElementType;
    completed: boolean | undefined;
    processing: boolean | undefined;
  };
  index: number;
  isLast: boolean;
  error?: string | null;
}

function ProcessItem({ step, index, isLast, error }: StepItemProps) {
  const IconComponent = step.icon;

  const getIcon = () => {
    if (error && step.processing)
      return <AlertCircle className="h-5 w-5 text-red-600" />;
    if (step.completed) return <Check className="h-5 w-5 text-green-600" />;
    if (step.processing)
      return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
    return <IconComponent className="h-5 w-5 text-muted-foreground" />;
  };

  const borderColor = cn(
    "flex items-start space-x-4 p-4 rounded-lg border transition-all duration-200",
    error &&
      step.processing &&
      "border-red-200 dark:border-red-800 bg-red-50/50 dark:bg-red-950/20",
    step.completed &&
      "border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20",
    step.processing &&
      "border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/20",
    !step.completed &&
      !step.processing &&
      !error &&
      "border-muted-foreground/20"
  );

  return (
    <div className="relative">
      {!isLast && (
        <div className="absolute left-6 top-12 w-0.5 h-8 bg-muted-foreground/20" />
      )}

      <div className={borderColor}>
        <div className="flex-shrink-0 mt-0.5">{getIcon()}</div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div>
              <p
                className={cn(
                  "font-semibold text-sm",
                  error && step.processing && "text-red-600 dark:text-red-400",
                  step.completed && "text-green-600 dark:text-green-400",
                  step.processing && "text-blue-600 dark:text-blue-400",
                  !step.completed && !step.processing && "text-muted-foreground"
                )}
              >
                {step.title}
              </p>
              <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
            </div>

            <div className="flex-shrink-0 ml-4">
              {error && step.processing && (
                <Badge variant={"destructive"}>Erro</Badge>
              )}

              {!error && step.processing && (
                <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  Em andamento...
                </Badge>
              )}
              {step.completed && (
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                  Concluído
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export {ProcessItem}