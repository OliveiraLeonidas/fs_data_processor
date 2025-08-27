import Link from "next/link";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, } from "./ui/sheet";
import  { DatabaseZap, Menu} from "lucide-react"
const Header = () => {
  return ( 
  
    <header className="w-full flex items-center h-18 md:h-16 p-4 border-b">
      
     <div className="w-full h-full md:hidden">
       <Sheet>
        <SheetHeader className="w-full flex flex-row items-baseline justify-between">
          <DatabaseZap/>
          <SheetTrigger><Menu/></SheetTrigger>
        </SheetHeader>
        <SheetContent className="py-16 px-8">
          <SheetTitle className="text-lg">Menu</SheetTitle>
            <div className="flex flex-col gap-6 capitalize">
              <Link href="/" className="cursor-pointer text-accent-foreground font-medium">ultimos scripts</Link>
              <Link href="/" className="cursor-pointer text-accent-foreground font-medium">ultimos arquivos CSV</Link>
            </div>
        </SheetContent>
      </Sheet>
     </div>

     <div className="w-full">
        <DatabaseZap/>
     </div>
    </header>
  );
}
 
export default Header;