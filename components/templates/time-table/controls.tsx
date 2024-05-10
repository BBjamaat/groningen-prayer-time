"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PrinterIcon } from "lucide-react";
import { createPortal } from "react-dom";

interface ControlsProps {
    value: string;
    setValue: (value: string) => void;
}

const Controls: React.FC<ControlsProps> = ({
    value, setValue
}) => {
    if (typeof window !== "object") return <div />;

    return createPortal((
        <div className="z-10 flex gap-2 fixed top-[50%] right-[10%] p-4 bg-white rounded-md shadow-md print:invisible max-lg:top-[1%] max-lg:right-[50%] max-lg:translate-x-1/2">
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