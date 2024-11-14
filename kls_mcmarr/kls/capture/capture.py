import uuid

from kls_mcmarr.mcmarr.capture.CaptureMcmarr import CaptureMcmarr as _Capture
from kls_mcmarr.kls.capture.mediapipe_wrapper.mediapipe_wrapper import RecordWithMediapipe

import time


class Capture(_Capture):

    def __init__(self, capture_mode="video", input_video_paths=None, camera_num=0, output_path="output/capture/",
                 show_output=False, formats_to_store=None):
        # If recording from camera, provide of camera parameters.
        self.camera_num = camera_num

        # If loading from video, provide of video path.
        self.video_path = None

        # Instantiate recorder.
        self.recorder = None

        # Recorder options.
        self.capture_mode = capture_mode
        self.input_video_paths = input_video_paths
        self.output_path = output_path
        self.show_output = show_output
        self.formats_to_store = formats_to_store
        pass

    def capture_movement(self, current_movement=0, uuid_name=uuid.uuid4(), autofocus=1):
        # Re-instantiate recorder to avoid "threads can only be started once" error.
        self.recorder = RecordWithMediapipe(self.capture_mode, self.input_video_paths[current_movement], self.camera_num, self.output_path,
                                            self.show_output, self.formats_to_store, autofocus, max_frames_to_capture=50)
        self.recorder.set_uuid_name(uuid_name)

        # Start recorder, and stop when finished (stop does a "join" operation).
        self.recorder.start()

        # If mode video, capture until thread finishes.
        if self.capture_mode == "video":
            self.recorder.join()
        # If mode camera, Capture during five seconds.
        else:
            # Wait until frame limit is set.
            self.recorder.frame_limit_reached.wait()

        # Stop recorder.
        self.recorder.stop()

        return self.recorder.get_captured_data_as_dataframe()
