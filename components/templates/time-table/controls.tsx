"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ImageIcon, PrinterIcon } from "lucide-react";
import { createPortal } from "react-dom";

interface ControlsProps {
    value: string;
    setValue: (value: string) => void;
}

const Controls: React.FC<ControlsProps> = ({
    value, setValue
}) => {
    if (typeof window !== "object") return null;

    return createPortal((
        <div className="z-10 flex gap-2 fixed bottom-[50%] right-[10%] p-4 bg-white rounded-md shadow-md print:invisible">
            <Input
                type="month"
                defaultValue={new Date().toISOString().split("T")[0].slice(0, 7)}
                value={value}
                onChange={(e) => setValue(e.target.value)}
            ></Input>
            <Button
                onClick={() => window.print()}
            >
                <PrinterIcon className="w-5 h-5" />
            </Button>
        </div>
    ), document.body)
}

export default Controls;