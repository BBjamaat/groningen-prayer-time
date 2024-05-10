import { Table, TableCaption, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table"
import { toTitleCase } from "@/lib/utils";
import moment from "moment-hijri";

interface Data {
    month: number;
    month_name: string;
    data: {
        day: number;
        fajr: string;
        sunrise: string;
        dhuhr: string;
        asr: string;
        maghrib: string;
        isha: string;
    }[];
}

interface DataTableProps {
    caption?: string;
    data: Data;
    year?: number;
}

const DataTable: React.FC<DataTableProps> = ({
    caption,
    data,
    year = new Date().getFullYear()
}) => {
    const month = toTitleCase(monthToDutch(data.month - 1));

    moment().format('iYYYY/iM/iD');

    const hijriMonths = getHijriMonths(year, data.month);
    const hijriYear = getHijriYear(year);

    return (
        <Table className="scale-[.8] -mt-24">
            <TableCaption>
                {caption?.split("\n").map((line, index) => <p key={index}>{line}</p>)}
            </TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead colSpan={2} className="text-center">
                        {month} <br />
                        {year}
                    </TableHead>
                    {CONSTS.map((item, index) => (<>
                        <TableHead key={index} className="w-[10%]">
                            {item.name}
                            <br />
                            <span className="text-xs float-right">{item.arabic}</span>
                        </TableHead>
                    </>))}
                    <TableHead colSpan={2} className="text-center">
                        {hijriMonths.map(m => <div key={m}>{m}</div>)}
                        {hijriYear}
                    </TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {data.data.map((item, index) => (
                    <TableRow key={index} className={
                        isFriday(item.day, data.month, year) ?
                            "bg-gray-200 font-semibold" : ""
                    }>
                        <TableCell className="p-1 w-1 text-center">
                            {getDayOfWeek(item.day, data.month, year, "nl-NL")}
                        </TableCell>
                        <TableCell className="p-1 w-1 text-center">
                            {item.day}
                        </TableCell>
                        {CONSTS.map((constItem, constIndex) => (
                            <TableCell className="py-1" key={constIndex}>
                                {
                                    // @ts-ignore
                                    item[constItem.id]
                                }
                            </TableCell>
                        ))}
                        <TableCell className="py-1 w-2 text-center">
                            {getDayOfWeek(item.day, data.month, year, "ar-SA")}
                        </TableCell>
                        <TableCell className="py-1 w-2 text-center">
                            {getHijriDay(item.day, data.month, year)}
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}

const CONSTS = [
    { id: "fajr", name: "Fajr", arabic: "الفجر" },
    { id: "sunrise", name: "Sunrise", arabic: "الشروق" },
    { id: "dhuhr", name: "Dhuhr", arabic: "الظهر" },
    { id: "asr", name: "Asr", arabic: "العصر" },
    { id: "maghrib", name: "Maghrib", arabic: "المغرب" },
    { id: "isha", name: "Isha", arabic: "العشاء" },
].reverse();

const getDayOfWeek = (day: number, month: number, year: number, locale: string) => {
    return new Date(year, month - 1, day).toLocaleDateString(
        locale,
        { weekday: 'short' }
    ).toUpperCase();
}

const isFriday = (day: number, month: number, year: number) => {
    return new Date(year, month - 1, day).getDay() === 5;
}

const getHijriDay = (day: number, month: number, year: number) => {
    return moment(`${year}-${month}-${day}`, 'YYYY-M-D').format('iD');
}

const getHijriYear = (year: number) => {
    return moment(`${year}`, 'YYYY').format('iYYYY');
}

const getHijriMonths = (year: number, month: number) => {
    const out: string[] = [];
    // check every day of the month
    for (let i = 1; i <= 31; i++) {
        const hijri = moment(`${year}-${month}-${i}`, 'YYYY-M-D');
        if (hijri.isValid()) {
            const month = hijri.format('iMMMM');
            if (!out.includes(month)) {
                out.push(month);
            }
        }
    }
    return out;
}

const monthToDutch = (month: number) => {
    const months = [
        "januari", "februari", "maart", "april", "mei", "juni",
        "juli", "augustus", "september", "oktober", "november", "december"
    ];
    return months[month];
}

export default DataTable;