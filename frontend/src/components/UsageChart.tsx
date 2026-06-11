import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts'

interface UsageChartProps {
  type: 'line' | 'bar' | 'donut' | 'cost'
  data: any[]
}

const COLORS = ['#7c3aed', '#3b82f6', '#06b6d4', '#f59e0b', '#ef4444', '#f472b6', '#10b981']

export function UsageChart({ type, data }: UsageChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-color)',
        }}
      >
        No historical data available for charts
      </div>
    )
  }

  // 1. Line/Area Chart for Daily Token Totals
  if (type === 'line') {
    return (
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="colorInput" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorOutput" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorCache" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="day" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-elevated)',
                borderColor: 'var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
              }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Area
              name="Input Tokens"
              type="monotone"
              dataKey="input_tokens"
              stroke="#7c3aed"
              fillOpacity={1}
              fill="url(#colorInput)"
            />
            <Area
              name="Output Tokens"
              type="monotone"
              dataKey="output_tokens"
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorOutput)"
            />
            <Area
              name="Cached Tokens"
              type="monotone"
              dataKey="cache_tokens"
              stroke="#06b6d4"
              fillOpacity={1}
              fill="url(#colorCache)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }

  // 2. Stacked Bar Chart for Per-Model Breakdown
  if (type === 'bar') {
    // Collect all unique model keys in the data set
    const modelKeysSet = new Set<string>()
    data.forEach((d) => {
      Object.keys(d).forEach((k) => {
        if (k !== 'day' && k !== 'total_tokens') {
          modelKeysSet.add(k)
        }
      })
    })
    const modelKeys = Array.from(modelKeysSet)

    return (
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <XAxis dataKey="day" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-elevated)',
                borderColor: 'var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
              }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            {modelKeys.map((model, idx) => (
              <Bar
                key={model}
                dataKey={model}
                name={model}
                stackId="a"
                fill={COLORS[idx % COLORS.length]}
                radius={[2, 2, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  // 3. Donut/Pie Chart for Token Share across all tools today
  if (type === 'donut') {
    return (
      <div style={{ width: '100%', height: 300, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ width: '100%', height: 240 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-elevated)',
                  borderColor: 'var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center', fontSize: '11px' }}>
          {data.map((item, index) => (
            <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: COLORS[index % COLORS.length],
                }}
              />
              <span style={{ color: 'var(--text-secondary)' }}>
                {item.name}: {Math.round(item.value).toLocaleString()} ({item.percentage}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // 4. Line Chart for USD Spend over time
  if (type === 'cost') {
    return (
      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="day" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <YAxis
              stroke="var(--text-muted)"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `$${v}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-elevated)',
                borderColor: 'var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
              }}
              formatter={(value: any) => [`$${parseFloat(value).toFixed(4)}`, 'Spend']}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Area
              name="USD Spend"
              type="monotone"
              dataKey="cost"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#colorCost)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return null
}
