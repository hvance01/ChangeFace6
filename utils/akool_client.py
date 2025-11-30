"""
Akool API Client for Video Face Swap
Documentation: https://docs.akool.com/ai-tools-suite/faceswap
"""

import requests
import time
import os
import uuid
from typing import Optional
from urllib.parse import urljoin


class AkoolAPIError(Exception):
    """Akool API error with code and message"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Akool API Error [{code}]: {message}")


class AkoolClient:
    """
    Akool API Client for video face swap

    Authentication: Uses x-api-key header (recommended method)
    API Base: https://openapi.akool.com
    """

    BASE_URL = "https://openapi.akool.com"
    FACE_DETECT_URL = "https://openapi.akool.com"

    # API Endpoints
    ENDPOINTS = {
        "video_faceswap": "/api/open/v3/faceswap/highquality/specifyvideo",
        "image_faceswap": "/api/open/v3/faceswap/highquality/specifyimage",
        "get_result": "/api/open/v3/faceswap/result/listbyids",
        "face_detect": "/interface/detect-api/detect_faces",
        "get_credit": "/api/open/v3/faceswap/quota/info",
    }

    # Status codes
    STATUS_PENDING = 1      # Processing
    STATUS_SUCCESS = 2      # Completed
    STATUS_FAILED = 3       # Failed

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Akool client

        Args:
            api_key: Akool API Key (get from https://akool.com -> API -> API Credentials)
            timeout: Request timeout in seconds (default 30)
        """
        if not api_key:
            raise ValueError("Akool API Key is required")

        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, base_url: str = None, retries: int = 3, **kwargs) -> dict:
        """
        Make API request with retry support

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint
            base_url: Optional base URL override
            retries: Number of retry attempts (default 3)
            **kwargs: Additional request arguments

        Returns:
            Response JSON data

        Raises:
            AkoolAPIError: If API returns error code
            requests.RequestException: If request fails after all retries
        """
        url = urljoin(base_url or self.BASE_URL, endpoint)
        kwargs.setdefault('timeout', self.timeout)

        last_exception = None
        for attempt in range(retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()

                data = response.json()

                # Check for API error (code != 1000)
                if data.get("code") != 1000:
                    raise AkoolAPIError(
                        code=data.get("code", -1),
                        message=data.get("msg", "Unknown error")
                    )

                return data

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

            except AkoolAPIError:
                # Don't retry API errors - they are intentional
                raise

        raise last_exception or Exception("Request failed after all retries")

    def detect_faces(self, media_url: str, media_type: str = "image") -> dict:
        """
        Detect faces in image or video to get landmarks

        Args:
            media_url: URL of the image or video
            media_type: "image" or "video"

        Returns:
            Face detection result with landmarks
        """
        payload = {
            "url": media_url,
        }

        # Add num_frames for video
        if media_type == "video":
            payload["num_frames"] = 1

        url = urljoin(self.FACE_DETECT_URL, self.ENDPOINTS["face_detect"])
        kwargs = {'timeout': self.timeout, 'json': payload}

        response = self.session.request("POST", url, **kwargs)
        response.raise_for_status()

        data = response.json()

        # Face detect API uses error_code 0 for success (different from other APIs)
        if data.get("error_code", 0) != 0:
            raise AkoolAPIError(
                code=data.get("error_code", -1),
                message=data.get("error_msg", "Face detection failed")
            )

        return data

    def swap_face_video(
        self,
        source_face_url: str,
        target_video_url: str,
        source_landmarks: str = None,
        target_face_url: Optional[str] = None,
        target_landmarks: Optional[str] = None,
        face_enhance: bool = True,
        webhook_url: Optional[str] = None
    ) -> dict:
        """
        Swap face in video (async operation)

        Args:
            source_face_url: URL of the face image to use as replacement
            target_video_url: URL of the target video
            source_landmarks: Face landmarks from detect_faces (REQUIRED by API)
            target_face_url: URL of the face image from video frame (optional, will use source if not provided)
            target_landmarks: Video face landmarks from detect_faces (optional)
            face_enhance: Whether to enhance face quality (recommended True for best results)
            webhook_url: Optional webhook URL for callback

        Returns:
            Response with job_id and _id for tracking

        Raises:
            ValueError: If source_landmarks is not provided
        """
        # API requires landmarks - must detect first if not provided
        if not source_landmarks:
            raise ValueError("source_landmarks is required. Use detect_faces() first to get landmarks.")

        # Use target_face_url if provided, otherwise use source_face_url
        target_url = target_face_url or source_face_url
        target_opts = target_landmarks or source_landmarks

        payload = {
            "sourceImage": [
                {
                    "path": source_face_url,
                    "opts": source_landmarks
                }
            ],
            "targetImage": [
                {
                    "path": target_url,
                    "opts": target_opts
                }
            ],
            "modifyVideo": target_video_url,
            "face_enhance": 1 if face_enhance else 0,
        }

        if webhook_url:
            payload["webhookUrl"] = webhook_url

        return self._request(
            "POST",
            self.ENDPOINTS["video_faceswap"],
            json=payload
        )

    def get_result(self, job_id: str) -> dict:
        """
        Get faceswap result by job ID

        Args:
            job_id: Job ID from swap_face_video response

        Returns:
            Result with status and output URL
        """
        return self._request(
            "GET",
            self.ENDPOINTS["get_result"],
            params={"_ids": job_id}
        )

    def get_credit_info(self) -> dict:
        """
        Get user credit balance information

        Returns:
            Credit info including remaining balance
        """
        return self._request("GET", self.ENDPOINTS["get_credit"])

    def wait_for_result(
        self,
        job_id: str,
        timeout: int = 600,
        poll_interval: int = 5,
        progress_callback=None
    ) -> str:
        """
        Wait for video processing to complete

        Args:
            job_id: Job ID from swap_face_video response
            timeout: Maximum wait time in seconds (default 10 minutes)
            poll_interval: Polling interval in seconds
            progress_callback: Optional callback function(status, message)

        Returns:
            Result video URL

        Raises:
            TimeoutError: If processing exceeds timeout
            AkoolAPIError: If processing fails
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_result(job_id)

            # Parse result - format: {"code": 1000, "data": {"result": [...]}}
            result_data = result.get("data", {})

            # Handle nested result structure
            if isinstance(result_data, dict):
                result_list = result_data.get("result", [])
            else:
                result_list = result_data if isinstance(result_data, list) else []

            if not result_list:
                if progress_callback:
                    progress_callback(self.STATUS_PENDING, "Waiting for processing to start...")
                time.sleep(poll_interval)
                continue

            item = result_list[0] if isinstance(result_list, list) else result_list
            status = item.get("faceswap_status", self.STATUS_PENDING)

            if status == self.STATUS_SUCCESS:
                video_url = item.get("url") or item.get("video")
                if video_url:
                    if progress_callback:
                        progress_callback(self.STATUS_SUCCESS, "Processing complete!")
                    return video_url

            elif status == self.STATUS_FAILED:
                error_msg = item.get("alg_msg") or item.get("error", "Processing failed")
                raise AkoolAPIError(status, error_msg)

            # Still processing
            if progress_callback:
                progress_callback(self.STATUS_PENDING, f"Processing video... (status: {status})")

            time.sleep(poll_interval)

        raise TimeoutError(f"Video processing timed out after {timeout} seconds")


def upload_to_temp_hosting(file_path: str) -> str:
    """
    Upload local file to temporary hosting for API access

    Since Akool API requires public URLs, we need to upload local files.
    This function uploads to a temporary file hosting service.

    Args:
        file_path: Local file path

    Returns:
        Public URL of the uploaded file

    Note:
        In production, you should use your own cloud storage (S3, GCS, OSS, etc.)
        This uses tmpfiles.org which keeps files for 1 hour minimum.
    """
    # Try multiple hosting services for reliability
    hosting_services = [
        _upload_to_tmpfiles,
        _upload_to_fileio,
    ]

    last_error = None
    for upload_func in hosting_services:
        try:
            return upload_func(file_path)
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Failed to upload file to any hosting service: {last_error}")


def _upload_to_tmpfiles(file_path: str) -> str:
    """Upload to tmpfiles.org (files kept for 1 hour minimum)"""
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://tmpfiles.org/api/v1/upload',
            files={'file': f}
        )

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            # Convert view URL to direct download URL
            # tmpfiles.org returns: https://tmpfiles.org/1234/file.mp4
            # We need: https://tmpfiles.org/dl/1234/file.mp4
            view_url = data.get('data', {}).get('url', '')
            if view_url:
                direct_url = view_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                return direct_url

    raise Exception(f"tmpfiles.org upload failed: {response.text}")


def _upload_to_fileio(file_path: str) -> str:
    """Upload to file.io (backup option, files deleted after download)"""
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://file.io',
            files={'file': f},
            data={'expires': '1d'}
        )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data.get('link')

    raise Exception(f"file.io upload failed: {response.text}")


def swap_face_akool(
    face_image_path: str,
    video_path: str,
    api_key: str = None,
    face_enhance: bool = True,
    progress_callback=None
) -> str:
    """
    High-level function to swap face in video using Akool API

    Args:
        face_image_path: Local path to face image
        video_path: Local path to target video
        api_key: Akool API Key (or set AKOOL_API_KEY env var)
        face_enhance: Enable face enhancement for better quality
        progress_callback: Optional callback for progress updates

    Returns:
        URL of the result video

    Example:
        result_url = swap_face_akool(
            face_image_path="face.jpg",
            video_path="video.mp4",
            api_key="your_api_key"
        )
    """
    # Validate input files exist
    if not os.path.exists(face_image_path):
        raise FileNotFoundError(f"Face image not found: {face_image_path}")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Get API key
    api_key = api_key or os.getenv("AKOOL_API_KEY")
    if not api_key:
        raise ValueError("Akool API Key is required. Set AKOOL_API_KEY env var or pass api_key parameter")

    # Initialize client
    client = AkoolClient(api_key)

    # Step 1: Upload files to get public URLs
    if progress_callback:
        progress_callback(0, "Uploading face image...")
    face_url = upload_to_temp_hosting(face_image_path)

    if progress_callback:
        progress_callback(1, "Uploading video...")
    video_url = upload_to_temp_hosting(video_path)

    # Step 2: Detect face landmarks (REQUIRED by API)
    if progress_callback:
        progress_callback(1, "Detecting face landmarks...")

    try:
        detect_result = client.detect_faces(face_url, "image")

        # Parse faces from response
        # Format: {"error_code": 0, "faces_obj": {"0": {"landmarks": [[[x,y],...]], "region": [...]}}}
        faces_obj = detect_result.get("faces_obj", {})
        if not faces_obj:
            raise Exception("No face detected in the source image. Please use a clear face photo.")

        # Get first frame's face data (key "0" for images)
        first_frame_key = list(faces_obj.keys())[0]
        first_frame = faces_obj[first_frame_key]

        # Get landmarks array - format: [[[x1,y1], [x2,y2], ...]]
        landmarks_list = first_frame.get("landmarks", [])
        if not landmarks_list or not landmarks_list[0]:
            raise Exception("Failed to get face landmarks. Please use a different photo.")

        # Convert landmarks to string format: "x1,y1:x2,y2:x3,y3:x4,y4:x5,y5"
        landmarks = landmarks_list[0]  # Get first face's landmarks
        source_landmarks = ":".join([f"{int(p[0])},{int(p[1])}" for p in landmarks])

    except AkoolAPIError as e:
        raise Exception(f"Face detection failed: {e.message}")

    # Step 3: Submit video face swap job
    if progress_callback:
        progress_callback(1, "Starting face swap processing...")

    result = client.swap_face_video(
        source_face_url=face_url,
        target_video_url=video_url,
        source_landmarks=source_landmarks,
        face_enhance=face_enhance
    )

    job_id = result.get("data", {}).get("_id")
    if not job_id:
        raise AkoolAPIError(-1, "No job ID returned from API")

    # Step 4: Wait for processing to complete
    def internal_callback(status, message):
        if progress_callback:
            progress_callback(status, message)

    result_url = client.wait_for_result(
        job_id=job_id,
        timeout=600,  # 10 minutes
        poll_interval=5,
        progress_callback=internal_callback
    )

    return result_url
