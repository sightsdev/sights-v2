/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MoveArmServoParams } from '../models/MoveArmServoParams';
import type { MoveMotorsParams } from '../models/MoveMotorsParams';
import type { SensorConfig } from '../models/SensorConfig';
import type { SwitchConfigBody } from '../models/SwitchConfigBody';
import type { UpdateConfigBody } from '../models/UpdateConfigBody';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DefaultService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Version
     * Get the current version.
     * @returns string Successful Response
     * @throws ApiError
     */
    public getVersionVersionGet(): CancelablePromise<string> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/version',
        });
    }
    /**
     * List Cameras
     * List all configured cameras.
     * @returns string Successful Response
     * @throws ApiError
     */
    public listCamerasCameraGet(): CancelablePromise<Array<string>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/camera/',
        });
    }
    /**
     * List Available Cameras
     * List all avaliable cameras currently on the host system
     * @returns number Successful Response
     * @throws ApiError
     */
    public listAvailableCamerasCameraAllGet(): CancelablePromise<Array<number>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/camera/all',
        });
    }
    /**
     * Drive
     * Move drive motors at provided speed
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public driveDrivePost(
        requestBody: MoveMotorsParams,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/drive/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Drive Stop
     * Stop all drive motors.
     * @returns any Successful Response
     * @throws ApiError
     */
    public driveStopDriveStopPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/drive/stop',
        });
    }
    /**
     * Sensor List
     * List all available sensors and their configurations.
     * @returns SensorConfig Successful Response
     * @throws ApiError
     */
    public sensorListSensorListGet(): CancelablePromise<Record<string, SensorConfig>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/sensor/list/',
        });
    }
    /**
     * Sensor Read
     * Read data from a specific sensor.
     * @param sensorId
     * @returns any Successful Response
     * @throws ApiError
     */
    public sensorReadSensorSensorIdGet(
        sensorId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/sensor/{sensor_id}',
            path: {
                'sensor_id': sensorId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Arm Move
     * Move a specific servo on the arm.
     * @param servoName
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public armMoveArmServoServoNamePost(
        servoName: string,
        requestBody: MoveArmServoParams,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/arm/servo/{servo_name}',
            path: {
                'servo_name': servoName,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Arm Home
     * Move arm to home position.
     * @returns any Successful Response
     * @throws ApiError
     */
    public armHomeArmHomePost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/arm/home',
        });
    }
    /**
     * Arm Preset
     * Move arm to a preset position.
     * @param preset
     * @returns any Successful Response
     * @throws ApiError
     */
    public armPresetArmPresetPresetPost(
        preset: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/arm/preset/{preset}',
            path: {
                'preset': preset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Power
     * Power off the system.
     * @returns string Successful Response
     * @throws ApiError
     */
    public powerPoweroffPost(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/poweroff',
        });
    }
    /**
     * Reboot
     * Reboot the system.
     * @returns string Successful Response
     * @throws ApiError
     */
    public rebootRebootPost(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/reboot',
        });
    }
    /**
     * Reload
     * Reload the application state from configuration.
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public reloadReloadPost(): CancelablePromise<Record<string, boolean>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/reload',
        });
    }
    /**
     * Get Logs
     * App log file
     * @returns string Successful Response
     * @throws ApiError
     */
    public getLogsLogsGet(): CancelablePromise<string> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/logs',
        });
    }
    /**
     * Ping Endpoint
     * Returns the current network delay (aka ping)
     * @returns number Successful Response
     * @throws ApiError
     */
    public pingEndpointPingGet(): CancelablePromise<Record<string, number>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/ping',
        });
    }
    /**
     * Estop
     * Emergency Stop - Use at own risk
     * @returns string Successful Response
     * @throws ApiError
     */
    public estopEstopPost(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/estop',
        });
    }
    /**
     * Get Active Config
     * Get the currently active config file name.
     * @returns string Successful Response
     * @throws ApiError
     */
    public getActiveConfigConfigActiveGet(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/config/active',
        });
    }
    /**
     * List Configs
     * List all available config files.
     * @returns string Successful Response
     * @throws ApiError
     */
    public listConfigsConfigListGet(): CancelablePromise<Record<string, Array<string>>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/config/list',
        });
    }
    /**
     * Get Config File
     * Get the contents of the currently active config file.
     * @returns string Successful Response
     * @throws ApiError
     */
    public getConfigFileConfigFileGet(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/config/file',
        });
    }
    /**
     * List Backups
     * List all backup files for the currently active config.
     * @returns any Successful Response
     * @throws ApiError
     */
    public listBackupsConfigBackupsGet(): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/config/backups',
        });
    }
    /**
     * Get Backup File
     * Get the contents of a specific backup file.
     * @param filename
     * @returns string Successful Response
     * @throws ApiError
     */
    public getBackupFileConfigBackupFilenameGet(
        filename: string,
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/config/backup/{filename}',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Switch Config
     * Switch to a different configuration file.
     * @param requestBody
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public switchConfigConfigSwitchPost(
        requestBody: SwitchConfigBody,
    ): CancelablePromise<Record<string, boolean>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/config/switch',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Config
     * Update the current configuration file.
     * @param requestBody
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public updateConfigConfigUpdatePost(
        requestBody: UpdateConfigBody,
    ): CancelablePromise<Record<string, boolean>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/config/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
