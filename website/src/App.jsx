import { io } from "socket.io-client"
import { useState, useEffect } from 'react'
import Logs from "./components/Logs"
import './index.css'

const WEB_HOST = "http://203.101.225.4:5500"
const sio = io(WEB_HOST)

function App() {
  const [unlocked, setUnlocked] = useState(false)
  const [refreshData, setRefreshData] = useState(Date.now())
  const [stateText, setStateText] = useState("Locked")

  useEffect(() => {
    // On unlock door event
    sio.on("unlock_door", unlock => {
      // Set unlock variable
      setUnlocked(unlock)

      if (unlock) {
        setStateText("Unlocked")
      }
      else {
        setStateText("Locked")
      }
    })
    sio.on("refresh_data", () => {
      setRefreshData(Date.now())
    })
    sio.on("update_logs", data => {
      console.log(data)
    })

  }, [])

  function toggle() {
    sio.emit("unlock_door")
  }

  return (
    <>

      <main className='flex flex-col min-h-screen pt-5 w-full items-center bg-neutral-100'>
        <h1 className='text-2xl font-semibold mb-10'>Smart Lock RFID Access Logs</h1>
        <section className='bg-white rounded px-12 flex flex-col items-center p-3'>
        <p className='text-lg'>Current status: <span className={unlocked ? "text-blue-800 font-bold" : "text-red-800 font-bold"}>{stateText}</span></p>
          <button onClick={toggle} type="submit" className='rounded bg-green-500 hover:bg-green-400 focus-visible:outline-2  my-3 px-4 py-1 text-white flex justify-center items-center'>Unlock</button>
          <Logs refreshData={refreshData} WEB_HOST={WEB_HOST}/>
        </section>
      </main>
    </>
  )
}

export default App
