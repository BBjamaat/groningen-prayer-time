"use client"

import A4Page from "./page-a4";
import DataTable from "./data-table";
import times from "@/assets/times.json";
import LogoHeader from "./logo-header";
import Controls from "./controls";
import { useState } from "react";

const TimeTable: React.FC = () => {
    const [date, setDate] = useState(new Date().toISOString().split("T")[0].slice(0, 7));

    return (
        <div className="flex justify-center items-center w-screen h-screen bg-gray-400">
            <A4Page id="page">
                <LogoHeader />
                <DataTable
                    year={dateToYear(date)}
                    data={times[dateToMonth(date)]}
                    caption={`Travertijnstraat 12, 9743 SZ Groningen, KvK Groningen: 73044687
                    Rekeningnummer/IBAN: NL78INGB 0009095082`}
                />
            </A4Page>
            <Controls
                value={date}
                setValue={setDate}
            />
        </div>
    );
}

const dateToYear = (date: string) => {
    return Number(date.split("-")[0]);
}

const dateToMonth = (date: string) => {
    return Number(date.split("-")[1]) - 1;
}

export default TimeTable;