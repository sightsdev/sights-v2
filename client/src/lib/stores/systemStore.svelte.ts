import { AppClient } from '$lib/api';

let connectionStatus = $state<'connected' | 'connecting' | 'disconnected'>('connecting');
let lastUpdate = $state<Date | null>(null);
let cpuPercent = $state(0);
let temperature = $state(0);
let memoryPercent = $state(0);
let memoryUsedGB = $state(0);
let memoryTotalGB = $state(0);
let diskPercent = $state(0);
let diskUsedGB = $state(0);
let diskTotalGB = $state(0);
let uptimeSeconds = $state(0);

let interval: ReturnType<typeof setInterval> | null = null;
let subscribers = 0;
let isFetching = false;

const updatePeriod = 1000;
const client = new AppClient();

async function fetchSystemMetrics() {
	if (isFetching) {
		return;
	}
	isFetching = true;
	try {
		const data = await client.default.sensorReadSensorSensorIdGet('system_info');
		cpuPercent = data.cpu_percent ?? 0;
		temperature = data.temperature ?? 0;
		memoryPercent = data.memory_percent ?? 0;
		memoryUsedGB = data.memory_used_gb ?? 0;
		memoryTotalGB = data.memory_total_gb ?? 0;
		diskPercent = data.disk_percent ?? 0;
		diskUsedGB = data.disk_used_gb ?? 0;
		diskTotalGB = data.disk_total_gb ?? 0;
		uptimeSeconds = data.uptime_seconds ?? 0;
		connectionStatus = 'connected';
		lastUpdate = new Date();
	} catch {
		connectionStatus = 'disconnected';
	} finally {
		isFetching = false;
	}
}

function subscribe() {
	subscribers++;
	if (subscribers === 1) {
		fetchSystemMetrics();
		interval = setInterval(() => fetchSystemMetrics(), updatePeriod);
	}
	return () => {
		subscribers--;
		if (subscribers === 0 && interval) {
			clearInterval(interval);
			interval = null;
		}
	};
}

const uptimeFormatted = $derived.by(() => {
	const hours = Math.floor(uptimeSeconds / 3600);
	const minutes = Math.floor((uptimeSeconds % 3600) / 60);
	const seconds = uptimeSeconds % 60;
	if (hours > 0) return `${hours}h ${minutes}m`;
	else if (minutes > 0) return `${minutes}m ${seconds}s`;
	else return `${seconds}s`;
});

const isHealthy = $derived.by(() => {
	return (
		connectionStatus === 'connected' &&
		cpuPercent < 90 &&
		temperature < 85 &&
		memoryPercent < 90 &&
		diskPercent < 90
	);
});

export const systemStore = {
	get connectionStatus() {
		return connectionStatus;
	},
	get lastUpdate() {
		return lastUpdate;
	},
	get cpuPercent() {
		return cpuPercent;
	},
	get temperature() {
		return temperature;
	},
	get memoryPercent() {
		return memoryPercent;
	},
	get memoryUsedGB() {
		return memoryUsedGB;
	},
	get memoryTotalGB() {
		return memoryTotalGB;
	},
	get diskPercent() {
		return diskPercent;
	},
	get diskUsedGB() {
		return diskUsedGB;
	},
	get diskTotalGB() {
		return diskTotalGB;
	},
	get uptimeSeconds() {
		return uptimeSeconds;
	},
	get uptimeFormatted() {
		return uptimeFormatted;
	},
	get isHealthy() {
		return isHealthy;
	},
	subscribe,
	refresh: fetchSystemMetrics
};
