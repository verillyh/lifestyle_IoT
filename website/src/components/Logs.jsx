import { useEffect, useState } from "react"

function Logs( { refreshData }) {
    const [logs, setLogs] = useState([])

    useEffect(() => {
        fetch("http://localhost:5500/logs")
            .then(response => 
                response.json()
            )
            .then(data => {
                console.log(data)
                setLogs(data.logs)
                console.log(data.logs)
            })
            .catch(err => {
                console.error("Something went wrong while fetching logs", err)
            })
    }, [refreshData])

    return (
        <section className="flex flex-col items-center">
            <h2 className="font-semibold text-xl mt-10 mb-5">Recent Logs</h2>
            <table className="min-w-max w-full border-fixed">
                <thead>
                    <tr className="border-solid border-neutral-500 border">
                        <th className="px-14">Timestamp</th>
                        <th className="px-8 border border-neutral-500 border-solid">UID</th>
                        <th className="px-8">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {logs.map(log => (
                        <tr key={log.id}>
                            <td className="text-center py-1 border border-neutral-500">{log.timestamp}</td>
                            <td className="text-center py-1 border border-neutral-500">{log.uid}</td>
                            <td className="text-center py-1 border border-neutral-500">{log.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    )
}

export default Logs