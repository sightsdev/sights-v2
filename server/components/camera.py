# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
# These are set because simplejpeg has no stub file, so this is needed to remove the warnings
import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol, cast

import cv2
import simplejpeg
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request

Scope = dict[str, object]
Message = dict[str, object]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class CameraConfig(BaseModel):
    width: int
    height: int
    framerate: int
    quality: int
    devices: dict[str, int]


class CameraParameters(BaseModel):
    source: int
    id: str
    framerate: int
    width: int
    height: int
    quality: int


class Camera:
    def __init__(self, parameters: CameraParameters):
        self.parameters: CameraParameters = parameters
        self.capture: cv2.VideoCapture = cv2.VideoCapture(parameters.source)

        if parameters.width != 0 and parameters.height != 0:
            _ = self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, parameters.width)
            _ = self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, parameters.height)

        if parameters.framerate != 0:
            _ = self.capture.set(cv2.CAP_PROP_FPS, parameters.framerate)

        if not self.capture.isOpened():
            raise RuntimeError("Could not start video.")

    async def frames(self):
        _, frame = self.capture.read()
        frame_bytes = simplejpeg.encode_jpeg(
            frame,
            quality=self.parameters.quality,
            colorspace="BGR",
            colorsubsampling="422",
            fastdct=True,
        )
        yield frame_bytes
        _ = await asyncio.sleep(0)


class CameraComponent:
    @staticmethod
    def list_available() -> list[int]:
        index = 0
        arr: list[int] = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        return arr

    @staticmethod
    async def stream(scope: Scope, receive: Receive, send: Send):
        class AppStateData(Protocol):
            cameras: dict[str, CameraParameters]

        class AppState(Protocol):
            data: AppStateData

        class App(Protocol):
            state: AppState

        class StrictRequest(Protocol):
            app: App
            path_params: dict[str, str]

        class Connection(Protocol):
            disconnected: bool

        class BoundReceive(Protocol):
            __self__: Connection

            def __call__(self) -> Awaitable[Message]: ...

        message = await receive()
        request = cast(StrictRequest, cast(object, Request(scope, receive)))

        camera_id: str = request.path_params["id"]

        try:
            camera = Camera(request.app.state.data.cameras[camera_id])
        except (KeyError, AttributeError):
            raise HTTPException(404)

        if message.get("type") == "http.request":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"Content-Type", b"multipart/x-mixed-replace; boundary=frame"]
                    ],
                }
            )

            bound_receive = cast(BoundReceive, cast(object, receive))

            while not bound_receive.__self__.disconnected:
                async for frame in camera.frames():
                    data = b"".join(
                        [
                            b"--frame\r\n",
                            b"Content-Type: image/jpeg\r\n\r\n",
                            frame,
                            b"\r\n",
                        ]
                    )
                    await send(
                        {"type": "http.response.body", "body": data, "more_body": True}
                    )
