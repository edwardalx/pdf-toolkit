import { FileOutput, ShieldCheck } from 'lucide-react';

export function BrandHeader() {
  return (
    <header className="flex h-[76px] items-center justify-between border-b border-[#e8eaf0]">
      <a className="inline-flex items-center gap-2.5 font-[Manrope,sans-serif] text-[19px] font-extrabold tracking-[-.7px] text-[#20283a] no-underline" href="#">
        <span className="grid h-8 w-8 place-items-center rounded-[10px] bg-[#324fc1] text-white shadow-[0_3px_7px_#314ec333]"><FileOutput size={19} /></span>
        <span>paperplane<span className="text-[#536ee0]">.</span></span>
      </a>
      <span className="flex items-center gap-1.5 rounded-full border border-[#e1ecdf] bg-[#edf4ed] px-[11px] py-[7px] text-xs text-[#617166] max-[650px]:p-2 max-[650px]:text-[0px]"><ShieldCheck size={14} className="text-[#588367] max-[650px]:h-4 max-[650px]:w-4" /> Private by design</span>
    </header>
  );
}
