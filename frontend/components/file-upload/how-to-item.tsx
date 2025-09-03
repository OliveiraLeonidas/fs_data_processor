
interface HowToItemProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

const HowToItem = ({ title, description, icon }: HowToItemProps) => {
  return (
    <>
      <div className="flex items-start space-x-3">
        <div className="bg-primary/10 p-2 rounded-lg">{icon}</div>
        <div>
          <p className="font-medium text-md">{title}</p>
          <p className="text-md text-muted-foreground">{description}</p>
        </div>
      </div>
    </>
  );
};

export default HowToItem;
