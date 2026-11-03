# Software-only fixtures

`camera.yaml` is synthetic pinhole geometry for a 640x480 image. The test creates
a red circle with a known center and radius in memory. These are deterministic
software inputs, not captured camera data or physical calibration.

No neural model or Hugging Face download is needed for this OpenCV color test.
The resource directory is copied from this code repository in step 4. It is
independent of robot CAD files under `models/`.
