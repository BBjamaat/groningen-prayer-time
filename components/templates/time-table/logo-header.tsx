const LogoHeader: React.FC = () => {
    return (<>
        <div className="flex justify-center items-center my-2">
            <img
                src="./rahma_logo.svg"
                alt="logo"
                className="w-24 h-24" />
            <div className="ml-4 flex flex-col justify-center font-semibold">
                <span className="text-xl text-green-500">
                    مؤسسة مسجد الرحمة في خرونينغن
                </span>
                <span className="text-base text-gray-500">
                    Stichting Moskee Al Rahma in Groningen
                </span>
            </div>
        </div >
    </>);
}

export default LogoHeader;