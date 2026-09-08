import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'Protolabs | Maple Plain Campus Study',description:'An evidence-led exterior reconstruction of the Protolabs headquarters with fixed views and reference comparisons.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
