import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toPng } from "html-to-image";
import { ImageDownIcon, PrinterIcon } from "lucide-react";

interface ControlsProps {
    value: string;
    setValue: (value: string) => void;
}

const Controls: React.FC<ControlsProps> = ({
    value, setValue
}) => {
    const htmlToImageConvert = () => {
        const element = document.getElementById("page");
        if (!element) return;

        toPng(element, { cacheBust: false })
            .then((dataUrl) => {
                const link = document.createElement("a");
                link.download = "prayer-times.png";
                link.href = dataUrl;
                link.click();
            })
            .catch((err) => {
                console.log(err);
            });
    };

    return (
        <div className="z-10 flex flex-col gap-2 fixed top-[50%] right-[10%] p-4 bg-white rounded-md shadow-md print:invisible max-lg:top-[1%] max-lg:right-[50%] max-lg:translate-x-1/2">
            <Input
                type="month"
                defaultValue={new Date().toISOString().split("T")[0].slice(0, 7)}
                value={value}
                onChange={(e) => setValue(e.target.value)}
            />
            <div className="w-full flex gap-2">
                <Button
                    className="flex-1"
                    onClick={() => window.print()}
                >
                    <PrinterIcon className="w-5 h-5" />
                </Button>
                <Button
                    className="flex-1"
                    onClick={() => htmlToImageConvert()}
                >
                    <ImageDownIcon className="w-5 h-5" />
                </Button>
            </div>
        </div>
    )
}

export default Controls;