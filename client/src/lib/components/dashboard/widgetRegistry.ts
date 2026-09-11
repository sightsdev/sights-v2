import type { Component } from 'svelte';

import CameraStream from '$lib/components/dashboard/CameraStream.svelte';
import CircleGraph from '$lib/components/dashboard/CircleGraph.svelte';
import LineGraph from '$lib/components/dashboard/LineGraph.svelte';
import PixelGrid from '$lib/components/dashboard/PixelGrid.svelte';

type GenericComponent = Component<Record<string, unknown>>;

export interface ConfigSchemaItem {
	key: string;
	label: string;
	type: string;
	required?: boolean;
	options?: string;
	placeholder?: string;
	min?: number;
	max?: number;
	step?: number;
}

export interface WidgetTypeDefinition {
	component: GenericComponent;
	label: string;
	defaultSize: { w: number; h: number };
	defaultConfig: Record<string, unknown>;
	configSchema: ConfigSchemaItem[];
}

export const WIDGET_TYPES: Record<string, WidgetTypeDefinition> = {
	camera: {
		component: CameraStream as unknown as GenericComponent,
		label: 'Camera Stream',
		defaultSize: { w: 580, h: 440 },
		defaultConfig: {
			cameraName: null
		},
		configSchema: [
			{
				key: 'cameraName',
				label: 'Camera',
				type: 'select',
				required: true,
				options: 'cameras'
			}
		]
	},

	circleGraph: {
		component: CircleGraph as unknown as GenericComponent,
		label: 'Circle Graph',
		defaultSize: { w: 280, h: 440 },
		defaultConfig: {
			title: 'Sensor',
			sensorName: null,
			series: '',
			suffix: '%',
			updatePeriod: 500
		},
		configSchema: [
			{
				key: 'title',
				label: 'Title',
				type: 'text',
				required: true,
				placeholder: 'Sensor'
			},
			{
				key: 'sensorName',
				label: 'Sensor',
				type: 'select',
				required: true,
				options: 'sensors'
			},
			{
				key: 'series',
				label: 'Data Series',
				type: 'text',
				required: true,
				placeholder: 'e.g. cpu_percent'
			},
			{
				key: 'suffix',
				label: 'Suffix',
				type: 'text',
				placeholder: '%'
			},
			{
				key: 'updatePeriod',
				label: 'Update Period (ms)',
				type: 'number',
				required: true,
				min: 100,
				max: 10000,
				step: 100
			}
		]
	},

	lineGraph: {
		component: LineGraph as unknown as GenericComponent,
		label: 'Line Graph',
		defaultSize: { w: 580, h: 440 },
		defaultConfig: {
			title: 'Sensor Data',
			sensorName: null,
			updatePeriod: 500,
			length: 20,
			series: []
		},
		configSchema: [
			{
				key: 'title',
				label: 'Title',
				type: 'text',
				required: true,
				placeholder: 'Sensor Data'
			},
			{
				key: 'sensorName',
				label: 'Sensor',
				type: 'select',
				required: true,
				options: 'sensors'
			},
			{
				key: 'updatePeriod',
				label: 'Update Period (ms)',
				type: 'number',
				required: true,
				min: 100,
				max: 10000,
				step: 100
			},
			{
				key: 'length',
				label: 'Data Points',
				type: 'number',
				required: true,
				min: 5,
				max: 100,
				step: 5
			},
			{
				key: 'series',
				label: 'Data Series (comma-separated)',
				type: 'array',
				required: true,
				placeholder: 'e.g. eCO2, TVOC'
			}
		]
	},

	pixelGrid: {
		component: PixelGrid as unknown as GenericComponent,
		label: 'Pixel Grid',
		defaultSize: { w: 580, h: 440 },
		defaultConfig: {
			sensorName: null,
			width: 32,
			height: 24,
			tempRange: [0, 30],
			hslRange: [0, 90],
			updatePeriod: 500
		},
		configSchema: [
			{
				key: 'sensorName',
				label: 'Sensor',
				type: 'select',
				required: true,
				options: 'sensors'
			},
			{
				key: 'width',
				label: 'Grid Width',
				type: 'number',
				required: true,
				min: 8,
				max: 256
			},
			{
				key: 'height',
				label: 'Grid Height',
				type: 'number',
				required: true,
				min: 8,
				max: 256
			},
			{
				key: 'tempRange',
				label: 'Temperature Range',
				type: 'range',
				min: -20,
				max: 100
			},
			{
				key: 'hslRange',
				label: 'Color Hue Range',
				type: 'range',
				min: 0,
				max: 360
			},
			{
				key: 'updatePeriod',
				label: 'Update Period (ms)',
				type: 'number',
				required: true,
				min: 100,
				max: 5000,
				step: 100
			}
		]
	}
};
