import { useEffect, useState } from "react"
import Visualizations from "./Visualizations"

function Logs( { WEB_HOST, refreshData }) {
    const [logs, setLogs] = useState([])
    const [allLogs, setAllLogs] = useState([]) 

    useEffect(() => {
 
        fetch(`${WEB_HOST}/logs?limit_num=22`)
            .then(response => response.json())
            .then(data => setLogs(data.logs))
            .catch(err => {
                console.error("Something went wrong while fetching logs", err)
            })

        fetch(`${WEB_HOST}/logs?limit_num=50`)
            .then(response => response.json())
            .then(data => setAllLogs(data.logs))
            .catch(err => {
                console.error("Something went wrong while fetching all logs", err)
            })
    }, [refreshData])

    return (
        <section className="flex flex-row items-start w-full justify-center gap-8">
            <div className="flex-1 max-w-xl">
                <h2 className="font-semibold text-xl mt-10 mb-5 text-center">Recent Logs</h2>
                <div className="bg-white rounded-lg shadow-lg p-4">
                    <table className="min-w-max w-full border-collapse">
                        <thead>
                            <tr className="bg-blue-100">
                                <th className="px-6 py-3 text-left text-xs font-bold text-blue-900 uppercase tracking-wider rounded-tl-lg">Timestamp</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">UID</th>
                                <th className="px-6 py-3 text-left text-xs font-bold text-blue-900 uppercase tracking-wider rounded-tr-lg">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log, idx) => (
                                <tr
                                    key={log.id}
                                    className={
                                        (idx % 2 === 0 ? "bg-gray-50" : "bg-white") +
                                        " hover:bg-blue-50 transition-colors"
                                    }
                                >
                                    <td className="px-6 py-2 border-b border-gray-200 text-sm text-gray-700">{log.timestamp}</td>
                                    <td className="px-6 py-2 border-b border-gray-200 text-sm text-gray-700">{log.uid}</td>
                                    <td className="px-6 py-2 border-b border-gray-200 text-sm font-semibold">
                                        <span className={
                                            log.status === "Granted"
                                                ? "text-green-600"
                                                : "text-red-600"
                                        }>
                                            {log.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            <div className="flex-1 max-w-xl">
                <Visualizations logs={allLogs} />
            </div>
        </section>
    )
}

export default Logs
