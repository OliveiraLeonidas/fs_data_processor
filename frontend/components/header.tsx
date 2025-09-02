import Link from "next/link";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, } from "./ui/sheet";
import  { DatabaseZap, Hexagon, Menu, Moon, Sun} from "lucide-react"
import { Button } from "./ui/button";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import { useTheme } from "next-themes";
const Header = () => {
  const {theme, setTheme} = useTheme()
  
  const handleApiHealthCheck = () => {
    const response = apiClient.healthCheck()
    if (!response) return 

    response.catch((err) => {toast.error(`API connection has not been reacheed: ${err}`) })
    response.then((res) => {
      return toast.success(`${res.message}`)
    })
  }

  return ( 
  
    <header className="w-full flex items-center h-18 md:h-16 p-4 mb-8 border-b shadow-sm shadow-slate-50/60">
      
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

     <div className="w-full flex items-center justify-between px-8">
        <Link href={"/"}><DatabaseZap/></Link>
        <div className="flex justify-center items-center">
          <Button 
            onClick={handleApiHealthCheck}
            className="cursor-pointer">
          <Hexagon/>
          <span className="capitalize text-xs ">api health</span>
        </Button>
        <div className="flex items-center justify-center gap-4">
          <Button variant={"ghost"} className="outline cursor-pointer" onClick={() => setTheme(theme === 'dark' ? 'light': 'dark')}>
            <span>{ theme === 'light' ? <Sun /> : <Moon />}</span></Button>
        </div>
        </div>
     </div>
    </header>
  );
}
 
export default Header;