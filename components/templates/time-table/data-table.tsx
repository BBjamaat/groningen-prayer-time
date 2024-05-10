import { Table, TableCaption, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table"
import { toTitleCase } from "@/lib/utils";
import moment, { Moment } from "moment-hijri";

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

    const DLSstart = getDLSstart(year);
    const DLSend = getDLSend(year);

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
                {data.data.map((item, index) => {
                    const rowDate = new Date(year, data.month - 1, item.day);
                    const isDLSchange = isDayLightSavingChange(rowDate, DLSstart, DLSend);
                    return (
                        <TableRow key={index} className={
                            isFriday(rowDate) ?
                                "bg-gray-200 font-semibold" : ""
                        }>
                            <TableCell className="p-1 w-1 text-center">
                                {getDayOfWeek(rowDate, "nl-NL")}
                                {isDLSchange ? "**" : ""}
                            </TableCell>
                            <TableCell className="p-1 w-1 text-center">
                                {item.day}
                            </TableCell>
                            {CONSTS.map((constItem, constIndex) => (
                                <TableCell className="py-1" key={constIndex}>
                                    {
                                        // @ts-ignore
                                        formatTime(item[constItem.id], rowDate, DLSstart, DLSend)
                                    }
                                </TableCell>
                            ))}
                            <TableCell className="py-1 w-2 text-center">
                                {getDayOfWeek(rowDate, "ar-SA")}
                            </TableCell>
                            <TableCell className="py-1 w-2 text-center">
                                {getHijriDay(rowDate)}
                            </TableCell>
                        </TableRow>
                    )
                })}
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

const getDayOfWeek = (date: Date, locale: string) => {
    return date.toLocaleDateString(
        locale,
        { weekday: 'short' }
    ).toUpperCase();
}

const isFriday = (date: Date) => {
    return date.getDay() === 5;
}

const getHijriDay = (date: Date) => {
    return moment(date).format('iD');
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

const isDayLightSavingTime = (date: Date, DLSstart: Moment, DLSend: Moment) => {
    return moment(date).isBetween(DLSstart, DLSend, "day", "[)");
}
const isDayLightSavingChange = (date: Date, DLSstart: Moment, DLSend: Moment) => {
    // check if the date is the day of the change
    return moment(date).isSame(DLSstart, "day") || moment(date).isSame(DLSend, "day");
}

const formatTime = (time: string, date: Date, DLSstart: Moment, DLSend: Moment) => {
    const [hour, minute] = time.split(":");
    if (isDayLightSavingTime(date, DLSstart, DLSend)) {
        return `${Number(hour) + 1}:${minute}`;
    }
    return time;
}

const getDLSstart = (year: number) => {
    // last sunday of march (31st)
    return moment().year(year).month(2).endOf("month").day("Sunday");
}

const getDLSend = (year: number) => {
    // last sunday of october (31st)
    return moment().year(year).month(9).endOf("month").day("Sunday");
}

export default DataTable;