import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

function Visualizations({ logs }) {

  const processLast7DaysData = () => {
    const last7Days = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      last7Days.push({
        date: dateStr,
        day: date.toLocaleDateString('en-US', { weekday: 'short' }),
        granted: 0,
        denied: 0,
        total: 0
      });
    }
    
    logs.forEach(log => {
      const logDate = log.timestamp.split('T')[0];
      const dayData = last7Days.find(day => day.date === logDate);
      
      if (dayData) {
        if (log.status === 'Granted') {
          dayData.granted++;
        } else {
          dayData.denied++;
        }
        dayData.total++;
      }
    });
    
    return last7Days;
  };

  const last7DaysData = processLast7DaysData();

  const processTodayByHour = () => {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    const hours = Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      granted: 0,
      denied: 0,
      total: 0
    }));

    logs.forEach(log => {
      const [date, time] = log.timestamp.split('T');
      if (date === todayStr) {
        const hour = parseInt(time.split(':')[0], 10);
        if (!isNaN(hour) && hour >= 0 && hour < 24) {
          if (log.status === 'Granted') {
            hours[hour].granted++;
          } else {
            hours[hour].denied++;
          }
          hours[hour].total++;
        }
      }
    });

    return hours.filter(h => h.total > 0);
  };

  const todayByHourData = processTodayByHour();

  return (
    <div className="mt-8">
      {/* Today's Activity by Hour (Line Chart) */}
      <div className="bg-white rounded px-6 py-4 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-center">Today's Activity by Hour</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={todayByHourData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="granted" 
              stroke="#10B981" 
              strokeWidth={3}
              name="Granted"
              dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="denied" 
              stroke="#EF4444" 
              strokeWidth={3}
              name="Denied"
              dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#3B82F6" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Total"
              dot={{ fill: '#3B82F6', strokeWidth: 2, r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 7-Day Activity Chart */}
      <div className="bg-white rounded px-6 py-4 mb-6">
        <h2 className="text-xl font-semibold mb-4 text-center">Last 7 Days Activity</h2>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={last7DaysData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="day" 
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(label) => `Day: ${label}`}
              formatter={(value, name) => [value, name === 'granted' ? 'Granted' : name === 'denied' ? 'Denied' : 'Total']}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="granted" 
              stroke="#10B981" 
              strokeWidth={3}
              name="Granted"
              dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="denied" 
              stroke="#EF4444" 
              strokeWidth={3}
              name="Denied"
              dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#3B82F6" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Total"
              dot={{ fill: '#3B82F6', strokeWidth: 2, r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded px-4 py-3 text-center">
          <div className="text-2xl font-bold text-blue-600">{logs.length}</div>
          <div className="text-sm text-gray-600">Total Attempts</div>
        </div>
        <div className="bg-white rounded px-4 py-3 text-center">
          <div className="text-2xl font-bold text-green-600">
            {logs.filter(log => log.status === 'Granted').length}
          </div>
          <div className="text-sm text-gray-600">Successful</div>
        </div>
        <div className="bg-white rounded px-4 py-3 text-center">
          <div className="text-2xl font-bold text-red-600">
            {logs.filter(log => log.status === 'Denied').length}
          </div>
          <div className="text-sm text-gray-600">Denied</div>
        </div>
        <div className="bg-white rounded px-4 py-3 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {new Set(logs.map(log => log.uid)).size}
          </div>
          <div className="text-sm text-gray-600">Unique Users</div>
        </div>
      </div>
    </div>
  );
}

export default Visualizations;