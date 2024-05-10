interface A4PageProps {
    children?: React.ReactNode;
    id?: string;
}

const A4Page: React.FC<A4PageProps> = ({ children, id }) => {
    return (
        <div
            className="bg-white shadow-lg aspect-[210/297] w-[210mm] h-[297mm] p-6 scale-[.7] rounded-md max-md:scale-[.5] max-sm:scale-[.3] print:scale-[1] print:p-0 print:shadow-none print:w-full print:h-full print:aspect-auto"
            id={id}
        >
            {children}
        </div>
    );
}

export default A4Page;